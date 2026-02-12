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
        magic = 0x1000 
        return self.gate.create_packet(magic, seq, policy_id, payload)

    def test_valid_packet(self):
        packet = self.create_valid_packet(policy_id=0x01)
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "forwarded")
        self.assertEqual(result["policy_id"], 0x01)

    def test_masked_policy_id(self):
        # Manually construct to verify masking logic
        seq = 0x12345678
        policy_id = 0x02
        masked_pid = policy_id ^ seq
        
        # Create packet with this specific seq and masked_pid
        packet = self.gate.create_packet(0x1000, seq, policy_id, b"")
        
        # Verify raw bytes
        header = packet[:16]
        _, _, _, raw_masked_pid, _ = struct.unpack('!HIIIH', header)
        self.assertEqual(raw_masked_pid, masked_pid)
        
        # Verify processing
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "forwarded")
        self.assertEqual(result["policy_id"], policy_id)

    def test_checksum_verification(self):
        # Create a valid packet
        packet = bytearray(self.create_valid_packet())
        
        # Corrupt the payload head (first 2 bytes affect checksum)
        packet[16] ^= 0xFF # Flip a bit in the first byte of payload
        
        result = self.gate.process_packet(bytes(packet))
        self.assertEqual(result["status"], "dropped")
        self.assertIn("Checksum Mismatch", result["reason"])

    def test_timestamp_window_expired(self):
        # Create a packet with old timestamp (more than 2 seconds ago)
        packet = self.create_valid_packet()
        
        # Manually inject old timestamp
        header = bytearray(packet[:16])
        # Unpack, Modify, Repack
        magic, seq, ts, mpid, cksum = struct.unpack('!HIIIH', header)
        
        # Set TS to 3 seconds ago (30,000,000 ticks)
        old_ts = (ts - 30000000) & 0xFFFFFFFF
        
        # Need to recalculate checksum for the modified header
        # Using internal helper for convenience, though in real attack this is harder
        # Here we want to test the TIMESTAMP logic, so we must provide valid checksum for the old TS
        # to ensure it fails on TIMESTAMP, not CHECKSUM.
        
        # Re-create packet with explicit old timestamp logic if possible, 
        # or just modify and fix checksum.
        # Let's use the create_packet helper but patch time.time
        
        # Easier: Modify source code momentarily? No.
        # Let's just recalculate the checksum manually here.
        header_parts = (magic, seq, old_ts, mpid)
        payload = packet[16:]
        new_cksum = self.gate.calculate_folded_checksum(header_parts, payload[:2])
        
        new_header = struct.pack('!HIIIH', magic, seq, old_ts, mpid, new_cksum)
        packet = new_header + payload
        
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")
        self.assertIn("Timestamp Replay/Expired", result["reason"])

    def test_timestamp_future_rejection(self):
        # Create a packet with future timestamp (more than 2 seconds ahead)
        packet = self.create_valid_packet()
        header = bytearray(packet[:16])
        magic, seq, ts, mpid, cksum = struct.unpack('!HIIIH', header)
        
        # Set TS to +3 seconds
        future_ts = (ts + 30000000) & 0xFFFFFFFF
        
        # Recalculate checksum
        header_parts = (magic, seq, future_ts, mpid)
        payload = packet[16:]
        new_cksum = self.gate.calculate_folded_checksum(header_parts, payload[:2])
        
        new_header = struct.pack('!HIIIH', magic, seq, future_ts, mpid, new_cksum)
        packet = new_header + payload
        
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")
        self.assertIn("Timestamp Replay/Expired", result["reason"])

    def test_invalid_msbv_lookup(self):
        # Policy ID 0xFF is not in MsBV
        packet = self.create_valid_packet(policy_id=0xFF)
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")
        self.assertIn("rejected by MsBV", result["reason"])

if __name__ == '__main__':
    unittest.main()
