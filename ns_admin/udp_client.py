#!/usr/bin/env python3
"""
UDP Hole Punching - Peer Client
This client registers with the rendezvous server and establishes P2P connections.
"""

import socket
import threading
import json
import time
import sys

class PeerClient:
    def __init__(self, peer_id, server_host, server_port=5000):
        self.peer_id = peer_id
        self.server_addr = (server_host, server_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))  # Bind to any available port
        self.local_port = self.sock.getsockname()[1]
        
        self.connected_peers = {}  # {peer_id: (ip, port)}
        self.running = True
        
        print(f"Peer '{peer_id}' started on local port {self.local_port}")
    
    def register(self):
        """Register with the rendezvous server"""
        msg = {
            'cmd': 'register',
            'peer_id': self.peer_id
        }
        self.sock.sendto(json.dumps(msg).encode(), self.server_addr)
        print(f"Registered with server at {self.server_addr}")
    
    def send_heartbeat(self):
        """Send periodic heartbeats to the server"""
        while self.running:
            try:
                msg = {
                    'cmd': 'heartbeat',
                    'peer_id': self.peer_id
                }
                self.sock.sendto(json.dumps(msg).encode(), self.server_addr)
                time.sleep(10)
            except:
                break
    
    def list_peers(self):
        """Request list of available peers from server"""
        msg = {'cmd': 'list'}
        self.sock.sendto(json.dumps(msg).encode(), self.server_addr)
    
    def connect_to_peer(self, target_id):
        """Initiate connection to another peer"""
        msg = {
            'cmd': 'connect',
            'peer_id': self.peer_id,
            'target_id': target_id
        }
        self.sock.sendto(json.dumps(msg).encode(), self.server_addr)
        print(f"Requesting connection to peer '{target_id}'...")
    
    def punch_hole(self, peer_addr):
        """Send initial packets to punch through NAT"""
        punch_msg = json.dumps({
            'type': 'punch',
            'peer_id': self.peer_id
        }).encode()
        
        # Send multiple packets to ensure hole punching
        for i in range(5):
            self.sock.sendto(punch_msg, peer_addr)
            time.sleep(0.1)
    
    def send_message(self, peer_id, message):
        """Send a message to a connected peer"""
        if peer_id not in self.connected_peers:
            print(f"Not connected to peer '{peer_id}'")
            return
        
        peer_addr = self.connected_peers[peer_id]
        msg = {
            'type': 'message',
            'from': self.peer_id,
            'text': message
        }
        self.sock.sendto(json.dumps(msg).encode(), peer_addr)
    
    def handle_incoming(self):
        """Handle incoming messages"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = json.loads(data.decode())
                
                # Response from server
                if addr == self.server_addr:
                    if msg.get('status') == 'registered':
                        endpoint = msg.get('your_endpoint')
                        print(f"Server sees us at {endpoint['ip']}:{endpoint['port']}")
                    
                    elif 'peers' in msg:
                        peers = msg['peers']
                        print("\nAvailable peers:")
                        for pid, info in peers.items():
                            if pid != self.peer_id:
                                print(f"  - {pid} ({info['ip']}:{info['port']})")
                    
                    elif msg.get('status') == 'found':
                        peer_endpoint = msg['peer_endpoint']
                        peer_addr = (peer_endpoint['ip'], peer_endpoint['port'])
                        print(f"Punching hole to {peer_addr}...")
                        self.punch_hole(peer_addr)
                    
                    elif msg.get('cmd') == 'incoming_connection':
                        peer_id = msg['peer_id']
                        peer_endpoint = msg['peer_endpoint']
                        peer_addr = (peer_endpoint['ip'], peer_endpoint['port'])
                        print(f"\nIncoming connection from '{peer_id}' at {peer_addr}")
                        print("Punching hole back...")
                        self.punch_hole(peer_addr)
                
                # Direct peer-to-peer messages
                else:
                    msg_type = msg.get('type')
                    
                    if msg_type == 'punch':
                        peer_id = msg.get('peer_id')
                        print(f"Received punch from '{peer_id}' at {addr}")
                        self.connected_peers[peer_id] = addr
                        
                        # Send acknowledgment
                        ack = json.dumps({
                            'type': 'ack',
                            'peer_id': self.peer_id
                        }).encode()
                        self.sock.sendto(ack, addr)
                        print(f"✓ Connected to '{peer_id}'!")
                    
                    elif msg_type == 'ack':
                        peer_id = msg.get('peer_id')
                        self.connected_peers[peer_id] = addr
                        print(f"✓ Connection established with '{peer_id}'!")
                    
                    elif msg_type == 'message':
                        sender = msg.get('from')
                        text = msg.get('text')
                        print(f"\n[{sender}]: {text}")
                        
            except Exception as e:
                if self.running:
                    print(f"Error: {e}")
    
    def interactive_shell(self):
        """Interactive command shell"""
        print("\nCommands:")
        print("  list              - List available peers")
        print("  connect <peer_id> - Connect to a peer")
        print("  send <peer_id> <message> - Send message to peer")
        print("  quit              - Exit")
        print()
        
        while self.running:
            try:
                cmd = input("> ").strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split(maxsplit=2)
                
                if parts[0] == 'list':
                    self.list_peers()
                
                elif parts[0] == 'connect' and len(parts) >= 2:
                    self.connect_to_peer(parts[1])
                
                elif parts[0] == 'send' and len(parts) >= 3:
                    self.send_message(parts[1], parts[2])
                
                elif parts[0] == 'quit':
                    self.running = False
                    break
                
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                self.running = False
                break
    
    def run(self):
        """Start the peer client"""
        self.register()
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        heartbeat_thread.start()
        
        # Start receiving thread
        recv_thread = threading.Thread(target=self.handle_incoming, daemon=True)
        recv_thread.start()
        
        time.sleep(0.5)  # Wait for registration
        
        # Run interactive shell
        self.interactive_shell()
        
        self.sock.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python peer_client.py <peer_id> <server_host>")
        print("Example: python peer_client.py Alice 192.168.1.100")
        sys.exit(1)
    
    peer_id = sys.argv[1]
    server_host = sys.argv[2]
    
    client = PeerClient(peer_id, server_host)
    client.run()


    24.94.185.82

    novus 73.217.240.123