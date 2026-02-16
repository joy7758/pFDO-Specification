import struct
import time
class FDOGate:
    def __init__(self, policy_file='Policy_Dictionary.json'):
        self._active_msbv = {1: 0, 2: 1, 3: 2, 4: 3}
        self.msbv_table = self._active_msbv
        self.default_security_level = 0
    def parse_header(self, header_bytes):
        if len(header_bytes) != 16:
            raise ValueError('Header must be exactly 16 bytes')
        (magic, epoch, fingerprint, masked_policy_id, rlcp_checksum) = struct.unpack('!HIIIH', header_bytes)
        policy_id = masked_policy_id ^ epoch
        rlcp_flags = rlcp_checksum >> 12 & 15
        checksum = rlcp_checksum & 4095
        return {'magic': magic, 'epoch': epoch, 'fingerprint': fingerprint, 'masked_policy_id': masked_policy_id, 'policy_id': policy_id, 'rlcp_flags': rlcp_flags, 'checksum': checksum, 'raw': header_bytes}
    def calculate_folded_checksum(self, header_parts, payload_head):
        (magic, epoch, fingerprint, masked_policy_id, rlcp_flags) = header_parts
        epoch_fold = epoch >> 16 ^ epoch & 65535
        fp_fold = fingerprint >> 16 ^ fingerprint & 65535
        pid_fold = masked_policy_id >> 16 ^ masked_policy_id & 65535
        xor_sum = magic ^ epoch_fold ^ fp_fold ^ pid_fold ^ rlcp_flags << 12
        if payload_head:
            payload_val = struct.unpack('!H', payload_head[:2])[0] if len(payload_head) >= 2 else payload_head[0] << 8
            xor_sum ^= payload_val
        return xor_sum & 4095
    def validate_segment(self, header_bytes, payload_bytes=b''):
        try:
            header = self.parse_header(header_bytes)
        except ValueError as e:
            return (False, str(e))
        header_parts = (header['magic'], header['epoch'], header['fingerprint'], header['masked_policy_id'], header['rlcp_flags'])
        expected_checksum = self.calculate_folded_checksum(header_parts, payload_bytes[:2])
        if expected_checksum != header['checksum']:
            return (False, f"Checksum Mismatch: expected {expected_checksum:#06x}, got {header['checksum']:#06x}")
        current_epoch = int(time.time() * 1000) & 4294967295
        received_epoch = header['epoch']
        diff = current_epoch - received_epoch & 4294967295
        if diff > 2147483647:
            diff -= 4294967296
        if abs(diff) > 2000:
            return (False, f'Epoch Replay/Expired: diff {diff} ticks')
        policy_id = header['policy_id']
        if policy_id not in self.msbv_table:
            return (False, f'Policy ID {policy_id:#0x} rejected by MsBV+ (Priority Arbitration Pipeline)')
        return (True, 'Header Valid')
    def atomic_epoch_switch(self, new_epoch_config=None):
        if new_epoch_config is not None:
            self._active_msbv = dict(new_epoch_config)
            self.msbv_table = self._active_msbv
    def process_packet(self, packet_bytes):
        if len(packet_bytes) < 16:
            return {'status': 'dropped', 'reason': 'Packet too short'}
        header_bytes = packet_bytes[:16]
        payload = packet_bytes[16:]
        (is_valid, msg) = self.validate_segment(header_bytes, payload)
        if is_valid:
            header = self.parse_header(header_bytes)
            return {'status': 'forwarded', 'policy_id': header['policy_id'], 'epoch': header['epoch']}
        return {'status': 'dropped', 'reason': msg}
    def create_packet(self, magic, sequence, policy_id, payload=b''):
        current_epoch = int(time.time() * 1000) & 4294967295
        dummy_fingerprint = 3735928559
        rlcp_flags = 0
        masked_pid = policy_id ^ current_epoch
        header_parts = (magic, current_epoch, dummy_fingerprint, masked_pid, rlcp_flags)
        checksum = self.calculate_folded_checksum(header_parts, payload[:2])
        final_checksum_field = rlcp_flags << 12 | checksum & 4095
        header = struct.pack('!HIIIH', magic, current_epoch, dummy_fingerprint, masked_pid, final_checksum_field)
        return header + payload