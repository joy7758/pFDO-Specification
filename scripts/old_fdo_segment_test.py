import unittest
import struct
import time
from fdo_gate import FDOGate

class TestFDOGate(unittest.TestCase):
    def setUp(self):
        self.gate = FDOGate()

    def create_valid_packet(self, policy_id=0x01, seq=100, payload=b"payload_data"):
        # Helper to create a valid packet using the gate's internal logic
        # Magic 0x1000 (Version 1, Type 0)
        # Note: 'seq' argument is ignored in v1.3.0 create_packet as it enforces current Epoch
        magic = 0x1000 
        return self.gate.create_packet(magic, seq, policy_id, payload)

    def test_valid_packet(self):
        packet = self.create_valid_packet(policy_id=0x01)
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "forwarded")
        self.assertEqual(result["policy_id"], 0x01)

    def test_masked_policy_id(self):
        # Create packet. epoch is determined inside create_packet
        policy_id = 0x02
        packet = self.gate.create_packet(0x1000, 0, policy_id, b"")
        
        # Verify raw bytes
        header = packet[:16]
        # v1.3.0 layout: Magic(H), Epoch(I), Fingerprint(I), MaskedPID(I), RLCP_Cksum(H)
        magic, epoch, fingerprint, raw_masked_pid, rlcp_checksum = struct.unpack('!HIIIH', header)
        
        # Verify masking logic: MaskedPID = PolicyID ^ Epoch
        expected_masked_pid = policy_id ^ epoch
        self.assertEqual(raw_masked_pid, expected_masked_pid)
        
        # Verify processing
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "forwarded")
        self.assertEqual(result["policy_id"], policy_id)
        self.assertEqual(result["epoch"], epoch)

    def test_checksum_verification(self):
        # Create a valid packet
        packet = bytearray(self.create_valid_packet())
        
        # Corrupt the payload head (first 2 bytes affect checksum)
        packet[16] ^= 0xFF # Flip a bit in the first byte of payload
        
        result = self.gate.process_packet(bytes(packet))
        self.assertEqual(result["status"], "dropped")
        self.assertIn("Checksum Mismatch", result["reason"])

    def test_epoch_replay_expired(self):
        # Test Epoch Expiration (v1.3.0)
        packet = self.create_valid_packet()
        
        # Manually inject old epoch
        header = bytearray(packet[:16])
        # Unpack, Modify, Repack
        magic, epoch, fingerprint, mpid, rlcp_checksum = struct.unpack('!HIIIH', header)
        
        # Extract RLCP flags
        rlcp_flags = (rlcp_checksum >> 12) & 0xF
        
        # Set Epoch to 3 seconds ago (3000 ms)
        old_epoch = (epoch - 3000) & 0xFFFFFFFF
        
        # Recalculate checksum for the old epoch
        header_parts = (magic, old_epoch, fingerprint, mpid, rlcp_flags)
        payload = packet[16:]
        new_checksum_val = self.gate.calculate_folded_checksum(header_parts, payload[:2])
        
        # Reconstruct RLCP+Checksum field
        new_rlcp_checksum = (rlcp_flags << 12) | (new_checksum_val & 0xFFF)
        
        new_header = struct.pack('!HIIIH', magic, old_epoch, fingerprint, mpid, new_rlcp_checksum)
        packet = new_header + payload
        
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")
        self.assertIn("Epoch Replay/Expired", result["reason"])

    def test_epoch_future_rejection(self):
        # Test Future Epoch Rejection
        packet = self.create_valid_packet()
        header = bytearray(packet[:16])
        magic, epoch, fingerprint, mpid, rlcp_checksum = struct.unpack('!HIIIH', header)
        
        rlcp_flags = (rlcp_checksum >> 12) & 0xF
        
        # Set Epoch to +3 seconds (3000 ms)
        future_epoch = (epoch + 3000) & 0xFFFFFFFF
        
        # Recalculate checksum
        header_parts = (magic, future_epoch, fingerprint, mpid, rlcp_flags)
        payload = packet[16:]
        new_checksum_val = self.gate.calculate_folded_checksum(header_parts, payload[:2])
        
        new_rlcp_checksum = (rlcp_flags << 12) | (new_checksum_val & 0xFFF)
        
        new_header = struct.pack('!HIIIH', magic, future_epoch, fingerprint, mpid, new_rlcp_checksum)
        packet = new_header + payload
        
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")
        self.assertIn("Epoch Replay/Expired", result["reason"])

    def test_invalid_msbv_lookup(self):
        # Policy ID 0xFF is not in MsBV+
        packet = self.create_valid_packet(policy_id=0xFF)
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")
        self.assertIn("rejected by MsBV+", result["reason"])

if __name__ == '__main__':
    unittest.main()
