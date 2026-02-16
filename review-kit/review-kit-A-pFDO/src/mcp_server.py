import sys
import json
import logging
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fdo_gate import FDOGate
logging.basicConfig(filename='mcp_server.log', level=logging.DEBUG)
gate = FDOGate(policy_file='Policy_Dictionary.json')
def read_message():
    try:
        line = sys.stdin.readline()
        if not line:
            return None
        return json.loads(line)
    except Exception as e:
        logging.error(f'Error reading message: {e}')
        return None
def send_message(msg):
    json.dump(msg, sys.stdout)
    sys.stdout.write('\n')
    sys.stdout.flush()
def handle_initialize(request_id):
    return {'jsonrpc': '2.0', 'id': request_id, 'result': {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'fdo-gate-mcp', 'version': '0.1.0'}}}
def handle_list_tools(request_id):
    return {'jsonrpc': '2.0', 'id': request_id, 'result': {'tools': [{'name': 'validate_segment', 'description': 'Validate a DOIP segment header against governance policies.', 'inputSchema': {'type': 'object', 'properties': {'header_hex': {'type': 'string', 'description': '16-byte header in hex format'}, 'payload_hex': {'type': 'string', 'description': 'Payload in hex format (optional)', 'default': ''}}, 'required': ['header_hex']}}, {'name': 'create_packet', 'description': 'Create a valid DOIP packet with governance header.', 'inputSchema': {'type': 'object', 'properties': {'magic': {'type': 'integer'}, 'sequence': {'type': 'integer'}, 'policy_id': {'type': 'integer'}, 'payload_hex': {'type': 'string', 'default': ''}}, 'required': ['magic', 'sequence', 'policy_id']}}]}}
def handle_call_tool(request, request_id):
    params = request.get('params', {})
    name = params.get('name')
    args = params.get('arguments', {})
    if name == 'validate_segment':
        try:
            header_hex = args.get('header_hex', '')
            payload_hex = args.get('payload_hex', '')
            if header_hex.startswith('0x'):
                header_hex = header_hex[2:]
            if payload_hex.startswith('0x'):
                payload_hex = payload_hex[2:]
            header_bytes = bytes.fromhex(header_hex)
            payload_bytes = bytes.fromhex(payload_hex) if payload_hex else b''
            (is_valid, msg) = gate.validate_segment(header_bytes, payload_bytes)
            if is_valid:
                logging.info(f'Layer 5 Allowed: Packet accepted. Msg: {msg}')
            else:
                logging.warning(f'Layer 5 BLOCK: Packet rejected. Reason: {msg}')
            return {'jsonrpc': '2.0', 'id': request_id, 'result': {'content': [{'type': 'text', 'text': json.dumps({'valid': is_valid, 'message': msg})}]}}
        except Exception as e:
            logging.error(f'Error in validate_segment: {e}')
            return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32603, 'message': str(e)}}
    elif name == 'create_packet':
        try:
            magic = args.get('magic')
            sequence = args.get('sequence')
            policy_id = args.get('policy_id')
            payload_hex = args.get('payload_hex', '')
            if payload_hex.startswith('0x'):
                payload_hex = payload_hex[2:]
            payload = bytes.fromhex(payload_hex) if payload_hex else b''
            packet = gate.create_packet(magic, sequence, policy_id, payload)
            return {'jsonrpc': '2.0', 'id': request_id, 'result': {'content': [{'type': 'text', 'text': packet.hex()}]}}
        except Exception as e:
            logging.error(f'Error in create_packet: {e}')
            return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32603, 'message': str(e)}}
    return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32601, 'message': f'Method {name} not found'}}
def main():
    while True:
        msg = read_message()
        if not msg:
            break
        method = msg.get('method')
        request_id = msg.get('id')
        logging.debug(f'Received method: {method}')
        if method == 'initialize':
            send_message(handle_initialize(request_id))
        elif method == 'notifications/initialized':
            pass
        elif method == 'tools/list':
            send_message(handle_list_tools(request_id))
        elif method == 'tools/call':
            send_message(handle_call_tool(msg, request_id))
        elif request_id:
            pass
if __name__ == '__main__':
    main()