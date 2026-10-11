# Phase 3: Network Fundamentals by Building (3-4 weeks)

Goal: understand networking below the abstraction line. Build in a lab you own (VM + host-only network).

## Lab setup
- [ ] VirtualBox/UTM + a Linux VM (Ubuntu/Kali) on a host-only or NAT network
- [ ] Install Wireshark; capture your own traffic and read it daily

## Projects (in order)
1. [ ] Echo server + client with raw `socket` (TCP, then UDP). Handle disconnects.
2. [ ] Multi-client chat server using `threading`, then rewrite with `asyncio`
3. [ ] TCP port scanner (connect scan): threaded/async, timeouts, banner grabbing. Run only against your VM.
4. [ ] Packet sniffer with Scapy: print src/dst/protocol; log DNS queries
5. [ ] Detect ARP spoofing / port scans in a live capture
6. [ ] pcap analyzer: read a .pcap, report top talkers, flag scan patterns and beaconing (regular-interval connections), export events as logs your Phase 2 tool can read
7. [ ] (Stretch) Implement a tiny DNS client by hand: build the UDP packet bytes yourself with `struct`

## Concepts to understand
- OSI vs TCP/IP layers; what each header contains
- TCP 3-way handshake, flags (SYN, ACK, RST, FIN), and what a SYN scan looks like
- DNS, ARP, DHCP, ICMP, TLS handshake
- Subnets, CIDR, NAT, routing basics
- Blocking vs non-blocking I/O

## Resources
- Beej's Guide to Network Programming: https://beej.us/guide/bgnet/
- Wireshark docs: https://www.wireshark.org/docs/
- Scapy: https://scapy.readthedocs.io
- Practice pcaps: https://www.malware-traffic-analysis.net
- Nmap book (free online): https://nmap.org/book/
- Book: *Computer Networking: A Top-Down Approach* (Kurose & Ross)
- Book: *Black Hat Python* (Seitz)
- Subnetting practice: https://www.subnetting.net
- Python docs: `socket`, `asyncio`, `struct`

## Done when
You can explain a Wireshark capture of a TCP connection from the first SYN to the FIN, byte by byte.
