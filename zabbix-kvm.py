#!/usr/local/bin/python3.5
import libvirt
import json
from optparse import OptionParser
def main():
  options = parse_args()
  if options.item=="discovery":
    uuid_list(options)
  elif options.item=="cpu":
    cpu(options)
  elif options.item=="mem":
    mem(options)
  elif options.item=="net_out":
    net_out(options)
  elif options.item=="net_in":
    net_in(options)
  elif options.item=="rd_bytes":
    rd_bytes(options)
  elif options.item=="wr_bytes":
    wr_bytes(options)


def parse_args():
  parser = OptionParser()
  valid_item = ["discovery", "cpu","mem","net_out","net_in","wr_bytes","rd_bytes"]
  parser.add_option("", "--item", dest="item", help="", action="store", type="string", default=None)
  parser.add_option("", "--uuid", dest="uuid", help="", action="store", type="string", default=None)
  (options, args) = parser.parse_args()
  if options.item not in valid_item:
    parser.error("Item has to be one of: "+", ".join(valid_item))
  return options
def kvm_connect():
  try:
    conn = libvirt.openReadOnly('qemu:///system')
  except:
    sys.stderr.write("There was an error connecting to the local libvirt daemon using '"+uri+"'.")
    exit(1)
  return conn
def uuid_list(options):
  conn = kvm_connect()
  r = {"data":[]}
  try:
    conn.listAllDomains(0)
  except:
    domains = []
    for dom_id in conn.listDomainsID():
      r['data'].append( {"{#DOMAINUUID}":conn.lookupByID(dom_id).UUIDString()} )
  else:
    for domain in conn.listAllDomains(0):
      r["data"].append( {"{#DOMAINUUID}":domain.UUIDString()} )
  print(json.dumps(r))
def cpu(options):
  conn = kvm_connect()
  cpunum=conn.lookupByUUIDString(options.uuid).info()[3]
  cpuusertime=conn.lookupByUUIDString(options.uuid).info()[4]
  r=cpuusertime/cpunum/10000000
  print(r)  
def mem(options):
  conn = kvm_connect()
  host=conn.lookupByUUIDString(options.uuid)
  r=(host.memoryStats()["available"]-host.memoryStats()["unused"])/host.memoryStats()["available"]*100
  print(r)
def net_out(options):
  conn = kvm_connect()
  host=conn.lookupByUUIDString(options.uuid)
  location=host.XMLDesc().find("<target dev=\'tap")
  tapname=host.XMLDesc()[location+13:location+27]
  print (host.interfaceStats("{0}".format(tapname))[4]*8)
def net_in(options):
  conn = kvm_connect()
  host=conn.lookupByUUIDString(options.uuid)
  location=host.XMLDesc().find("<target dev=\'tap")
  tapname=host.XMLDesc()[location+13:location+27]
  print (host.interfaceStats("{0}".format(tapname))[0]*8)
def rd_bytes(options):
  conn = kvm_connect()
  host=conn.lookupByUUIDString(options.uuid)
  r=host.blockStatsFlags("vda")['rd_bytes']
  print(r)
def wr_bytes(options):
  conn = kvm_connect()
  host=conn.lookupByUUIDString(options.uuid)
  r=host.blockStatsFlags("vda")['wr_bytes']
  print(r)
if __name__ == "__main__":
  main()
