# ss-pretty
Python script to display socket statistics (from ss) in a columnar format

# Usage
`ss` output can be a big long string of info, and is hard to follow if you're watching a stream:
```bash
$ ss -tmi "src 203.0.113.254:80"
State                     Recv-Q                      Send-Q                                               Local Address:Port                                                Peer Address:Port
ESTAB                     0                           2146808                                            203.0.113.254:80                                             198.51.100.1:35882
         skmem:(r0,rb374400,t95744,tb9522176,f271616,w6454016,o0,bl0,d0) cubic wscale:10,10 rto:212 rtt:10.689/0.883 mss:1448 pmtu:1500 rcvmss:536 advmss:1448 cwnd:592 ssthresh:562 bytes_acked:258948616 segs_out:179298 segs_in:1090 data_segs_out:179298 send 641.6Mbps lastrcv:2824 pacing_rate 769.9Mbps delivery_rate 536.6Mbps busy:2768ms rwnd_limited:8ms(0.3%) unacked:456 retrans:0/6 rcv_space:28960 rcv_ssthresh:28960 notsent:1486520 minrtt:4.46

$ ss -tmi "src 203.0.113.254:80"
State                     Recv-Q                      Send-Q                                               Local Address:Port                                                Peer Address:Port
ESTAB                     0                           1592568                                            203.0.113.254:80                                             198.51.100.1:35882
         skmem:(r0,rb374400,t121856,tb9522176,f1922048,w4787200,o0,bl0,d0) cubic wscale:10,10 rto:212 rtt:10.662/0.809 mss:1448 pmtu:1500 rcvmss:536 advmss:1448 cwnd:752 ssthresh:562 bytes_acked:575517448 segs_out:397951 segs_in:2372 data_segs_out:397951 send 817.0Mbps lastrcv:6744 lastack:4 pacing_rate 980.4Mbps delivery_rate 901.0Mbps busy:6688ms rwnd_limited:8ms(0.1%) unacked:484 retrans:0/6 rcv_space:28960 rcv_ssthresh:28960 notsent:891736 minrtt:4.356
```

`ss-pretty` displays a columnar format and updates regularly so you can watch it:
```bash
$ prettySS.py -f "src 203.0.113.254:80" -u 0.5
timestamp       mss  rcvmss advmss rto  rtt             cwnd   ssthresh  bytes_acked  unacked retrans send       pacing_rate delivery_rate busy   rcv_space notsent
17:35:00.405289 1448 536    1448   208  10.198/5.099    10     581                                    11.4Mbps   22.7Mbps                         28960
17:35:00.922610 1448 536    1448   212  11.217/0.979    1042   581       41063832     619             1076.1Mbps 1291.3Mbps  925.5Mbps     456ms  28960     638256
17:35:01.441896 1448 536    1448   212  11.225/0.978    1042   581       99316872     810             1075.3Mbps 1290.3Mbps  877.6Mbps     976ms  28960     959976
17:35:01.961606 1448 536    1448   212  11.14/0.813     1096   581       158230200    738             1139.7Mbps 1367.6Mbps  813.0Mbps     1496ms 28960     1002232
17:35:02.480419 1448 536    1448   212  10.921/1.041    805    770       209615376    475     0/3     853.9Mbps  1024.6Mbps  804.7Mbps     2016ms 28960     1247032
```

It's the equivalent to running `ss -tmi`.
