Create the setup
```
make up
```
Verify
```
docker ps
CONTAINER ID        IMAGE                   COMMAND                  CREATED             STATUS              PORTS                                          NAMES
094792cce5ce        grafana/grafana:7.0.3   "/run.sh"                6 minutes ago       Up 6 minutes        0.0.0.0:3000->3000/tcp                         grafana
05e92731ae2c        telegraf:1.14.3         "/entrypoint.sh tele…"   6 minutes ago       Up 6 minutes        8092/udp, 8125/udp, 8094/tcp                   telegraf
ccea415c7d6a        influxdb:1.8.0          "/entrypoint.sh infl…"   6 minutes ago       Up 6 minutes        0.0.0.0:8086->8086/tcp                         influxdb
79f17f74aee0        ceosimage:4.23.3M       "/sbin/init systemd.…"   8 minutes ago       Up 8 minutes        0.0.0.0:2003->22/tcp, 0.0.0.0:6033->6030/tcp   ceos3
7f75c5392198        ceosimage:4.23.3M       "/sbin/init systemd.…"   8 minutes ago       Up 8 minutes        0.0.0.0:2002->22/tcp, 0.0.0.0:6032->6030/tcp   ceos2
7a91444b5e22        ceosimage:4.23.3M       "/sbin/init systemd.…"   8 minutes ago       Up 8 minutes        0.0.0.0:2001->22/tcp, 0.0.0.0:6031->6030/tcp   ceos1 
```
```
make ceos2-cli 
==========================================
start a cli session in the ceos2 container
==========================================
docker exec -i -t ceos2 Cli
ceos2>show ip bgp summary 
BGP summary information for VRF default
Router identifier 2.2.2.2, local AS number 65002
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.0.0.0         4  65001             13        13    0    0 00:05:57 Estab   4      4
  10.0.0.3         4  65003             11        11    0    0 00:05:57 Estab   5      5
ceos2>exit
```
```
make telegraf-logs 
==========================================================
fetch the 100 last lines of logs of the telegraf container
==========================================================
docker logs telegraf --tail 100
2020-06-15T01:15:06Z I! Starting Telegraf 1.14.3
2020-06-15T01:15:06Z I! Using config file: /etc/telegraf/telegraf.conf
2020-06-15T01:15:06Z I! Loaded inputs: cisco_telemetry_gnmi cisco_telemetry_gnmi
2020-06-15T01:15:06Z I! Loaded aggregators: 
2020-06-15T01:15:06Z I! Loaded processors: 
2020-06-15T01:15:06Z I! Loaded outputs: influxdb
2020-06-15T01:15:06Z I! Tags enabled: host=05e92731ae2c
2020-06-15T01:15:06Z I! [agent] Config: Interval:10s, Quiet:false, Hostname:"05e92731ae2c", Flush Interval:10s
```
Query InfluxDB with CLI
```
make influxdb-cli
=============================================
start a cli session in the influxdb container
=============================================
docker exec -it influxdb bash
root@ccea415c7d6a:/# influx
Connected to http://localhost:8086 version 1.8.0
InfluxDB shell version: 1.8.0
> SHOW DATABASES
name: databases
name
----
arista
_internal
> USE arista
Using database arista
>  
> SHOW MEASUREMENTS 
name: measurements
name
----
eos_bgp
eos_ipv4_route
ifcounters
openconfig_bgp
> 
> SHOW TAG KEYS FROM "ifcounters"
name: ifcounters
tagKey
------
host
name
source
> SHOW TAG VALUES FROM "ifcounters" with KEY = "name"
name: ifcounters
key  value
---  -----
name Ethernet1
name Ethernet2
name Ethernet3
> SHOW TAG VALUES FROM "ifcounters" with KEY = "source"
name: ifcounters
key    value
---    -----
source ceos1
source ceos2
source ceos3
> 
> SELECT "in_octets" FROM "ifcounters" WHERE ("name" =~/Ethernet(2|3)/) GROUP BY "source", "name" ORDER BY DESC LIMIT 1
name: ifcounters
tags: name=Ethernet3, source=ceos3
time                in_octets
----                ---------
1592184057166837080 2538

name: ifcounters
tags: name=Ethernet3, source=ceos2
time                in_octets
----                ---------
1592184057208175010 2328

name: ifcounters
tags: name=Ethernet3, source=ceos1
time                in_octets
----                ---------
1592184057170719054 2253

name: ifcounters
tags: name=Ethernet2, source=ceos3
time                in_octets
----                ---------
1592184057170511827 2608

name: ifcounters
tags: name=Ethernet2, source=ceos2
time                in_octets
----                ---------
1592184060543355778 2775

name: ifcounters
tags: name=Ethernet2, source=ceos1
time                in_octets
----                ---------
1592184060542884011 2421
> 
> SELECT "neighbors/neighbor/state/neighbor_address" AS "neighbor_address", "neighbors/neighbor/state/session_state" AS "session_state", "neighbors/neighbor/config/peer_as" AS "peer-as", "neighbors/neighbor/config/enabled" AS "peer_enabled" FROM "openconfig_bgp" GROUP BY "source", "neighbor_address" ORDER BY DESC LIMIT 4
name: openconfig_bgp
tags: neighbor_address=10.0.0.5, source=ceos3
time                neighbor_address session_state peer-as peer_enabled
----                ---------------- ------------- ------- ------------
1592183695265868394                                        true
1592183695263611340                                65001   
1592183695253546076 10.0.0.5                               
1592183695253365127                  ESTABLISHED           

name: openconfig_bgp
tags: neighbor_address=10.0.0.4, source=ceos1
time                neighbor_address session_state peer-as peer_enabled
----                ---------------- ------------- ------- ------------
1592183688383234793                  ESTABLISHED           
1592183688379572644                                        true
1592183688371928955                                65003   
1592183688269292047 10.0.0.4                               

name: openconfig_bgp
tags: neighbor_address=10.0.0.3, source=ceos2
time                neighbor_address session_state peer-as peer_enabled
----                ---------------- ------------- ------- ------------
1592183694317505417                                        true
1592183694315536471                                65003   
1592183694302870196 10.0.0.3                               
1592183694302804482                  ESTABLISHED           

name: openconfig_bgp
tags: neighbor_address=10.0.0.2, source=ceos3
time                neighbor_address session_state peer-as peer_enabled
----                ---------------- ------------- ------- ------------
1592183695275671333                                        true
1592183695270487426                                65002   
1592183695262307958 10.0.0.2                               
1592183695262188558                  ESTABLISHED           

name: openconfig_bgp
tags: neighbor_address=10.0.0.1, source=ceos1
time                neighbor_address session_state peer-as peer_enabled
----                ---------------- ------------- ------- ------------
1592183688382611560                  ESTABLISHED           
1592183688281551195                                        true
1592183688278341194                                65002   
1592183688173369759 10.0.0.1                               

name: openconfig_bgp
tags: neighbor_address=10.0.0.0, source=ceos2
time                neighbor_address session_state peer-as peer_enabled
----                ---------------- ------------- ------- ------------
1592183694322440248                                        true
1592183694318198046                                65001   
1592183694311901742 10.0.0.0                               
1592183694311713694                  ESTABLISHED           
> 
> SELECT "vrfBgpPeerInfoStatusEntryTable/default/bgpPeerInfoStatusEntry/10.0.0.1/bgpPeerEstablishedTime" AS "bgpPeerEstablishedTime", "vrfBgpPeerInfoStatusEntryTable/default/bgpPeerInfoStatusEntry/10.0.0.1/bgpPeerEstablishedTransitions" AS "bgpPeerEstablishedTransitions" FROM "eos_bgp" WHERE source='ceos1' ORDER BY DESC LIMIT 1
name: eos_bgp
time                bgpPeerEstablishedTime bgpPeerEstablishedTransitions
----                ---------------------- -----------------------------
1592183671302996650 1592172991.980566      1
> 
> 
> exit
root@ccea415c7d6a:/# exit
exit
```
Query InfluxDB with Python
```
python test.py 
3093
2934
2775
```
Use Grafana. 
You can now use the Grafana GUI http://localhost:3000
The default username and password are admin/admin, but we changed them to arista/arista
The datasource is already configured. It uses InfluxDB.
