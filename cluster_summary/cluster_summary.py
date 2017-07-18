#!/usr/bin/env python
# VMware vSphere Python SDK

"""
Python program for listing VMware config and summary data via vCenter host
Based on : https://github.com/vmware/pyvmomi/blob/master/sample/getallvms.py
"""

from __future__ import print_function
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import argparse
import atexit
import getpass
import requests
import ssl

def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(
       description='Process args for retrieving VMware infor via vCenter')
   parser.add_argument('-s', '--host', required=True, action='store',
                       help='Remote host to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to host')
   args = parser.parse_args()
   return args

def GetBase(si, content):
    print("Getting Base ...")
    print("\tBorn         : "+str(si.serverClock))
    Base = [item for item in content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], recursive=True).view]
    for item in Base:
       print("\tDatacenter   : "+item.name)
       print("\tStatus       : "+item.overallStatus)

def GetSummary(content):
    summary = [item for item in content.viewManager.CreateContainerView(content.rootFolder, [vim.ClusterComputeResource], recursive=True).view]
    for cluster_obj in summary:
       print("\tCluster      : "+cluster_obj.name)
       print("\tStatus       : "+cluster_obj.overallStatus)	
       print("\tCPU Cores    : "+str(cluster_obj.summary.numCpuCores))
       print("\tCpu(MHz)     : "+str(cluster_obj.summary.totalCpu))
       print("\tCpuUse(MHz)  : "+str(cluster_obj.summary.usageSummary.cpuDemandMhz))
       print("\tMem(GB)      : "+str(cluster_obj.summary.totalMemory / 1024 /1024 /1024)) 
       print("\tMemUse(GB)   : "+str(cluster_obj.summary.usageSummary.memDemandMB / 1024))

def GetAlarms(content):
    print("Getting Alarms ...")
    containerView = content.viewManager.CreateContainerView(content.rootFolder,[vim.Datacenter],True)
    children = containerView.view
    for child in children:
      alarms = child.triggeredAlarmState
      if len(alarms) == 0:
             print('No Alarms',)
      else:
         for alarm in alarms:
            if isinstance(alarm, vim.alarm.AlarmState):
              print("\tTarget      : "+str(alarm.entity.name)) 
              print("\tStatus      : "+str(alarm.overallStatus)) 
              print("\tTime        : "+str(alarm.time)) 
              print("\tText        : "+str(alarm.alarm.info.name))
              print("\tDescription : "+str(alarm.alarm.info.description))

def GetHosts(content):
    print("Getting Hosts ...")
    host_view = content.viewManager.CreateContainerView(content.rootFolder,[vim.HostSystem],True)
    print("\t Name,\t State,\tMem(GB),\tMemUse(GB),\tCpuSoc,\tCpuCorsSoc,\tCpuUse(MHz),\tTotMHz,\tUpTime(d),")
    for host in host_view.view:
      State = host.runtime.powerState
      Mem = (host.summary.hardware.memorySize / 1024 / 1024 / 1024)
      MemUse = (host.summary.quickStats.overallMemoryUsage / 1024)
      CpuP = host.summary.hardware.numCpuPkgs
      CpuC = host.summary.hardware.numCpuCores
      CpuU = host.summary.quickStats.overallCpuUsage
      CpuM = (host.summary.hardware.cpuMhz * host.summary.hardware.numCpuCores)
      UpTime = (host.summary.quickStats.uptime / 86400) 
      print ("\t",host.name+",\t"+State+",\t"+str(Mem)+",\t"+str(MemUse)+",\t"+str(CpuP)+",\t"+str(CpuC)+",\t"+str(CpuU)+",\t"+str(CpuM)+",\t"+str(UpTime))

def GetVMs(content):
    print("Getting VMs ...")
    print("\t Name,\tState,\tMem(MB),\tMemUse(MB),\tCpu#,\tCpuUse(MHz),\tUpTime(d),")
    vm_view = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    for vm in vm_view.view:
      State = vm.runtime.powerState
      Mem = vm.config.hardware.memoryMB
      MemUse = vm.summary.quickStats.guestMemoryUsage
      Cpu = vm.config.hardware.numCPU
      CpuUse = vm.summary.quickStats.overallCpuUsage
      UpTime = (vm.summary.quickStats.uptimeSeconds / 86400)
      print("\t",vm.name+",\t"+State+",\t"+str(Mem)+",\t"+str(MemUse)+",\t"+str(Cpu)+",\t"+str(CpuUse)+",\t"+str(UpTime))

def GetVMonHost(content):
    print("Getting VMs running on Hosts ...")
    containerView = content.viewManager.CreateContainerView(content.rootFolder,[vim.ClusterComputeResource],True)
    children = containerView.view
    for child in children:
      hosts = child.host
      for host in hosts:
         print("\tHost name : "+host.name)
         if hasattr(host, 'vm'):
            print("\tVMs running on host :")
            for vm in host.vm:
               print("\t\t"+vm.name)
         else:
            print("\tNo VMs ruiining on hosts")

def GetClusterRules(content):
    print("Getting Cluster rules ...")
    print("\t Name,\tType,\tVMGroup,\AffinetHostGroup,\tAntiAffinetHostGroup#,\tEnabled,") 
    containerView = content.viewManager.CreateContainerView(content.rootFolder,[vim.ClusterComputeResource],True)
    children = containerView.view
    for child in children:
      rules = child.configuration.rule
      if len(rules) == 0:
             print('No Cluster rules set',)
      else:
         for rule in rules:
            if isinstance(rule, vim.cluster.VmHostRuleInfo):
               print("\t"+rule.name+",\t""VmHostRule"",\t"+rule.vmGroupName+",\t"+rule.affineHostGroupName+",\t"+str(rule.antiAffineHostGroupName)+",\t"+str(rule.enabled))
            else:
               if isinstance(rule, vim.cluster.AntiAffinityRuleSpec):
                  type = 'AntiAffinityRule'
               else:
                  type = 'AffinityRule'
               print("\t"+rule.name+",\t"+type+",\t"+",\t"+",\t"",\t"+str(rule.enabled))
               print("\t\tVMs in the rule :")
               for vm in rule.vm:
                  print("\t\t" + vm.name)

def GetClusterGroups(content):
    print("Getting Cluster groups ...")
    containerView = content.viewManager.CreateContainerView(content.rootFolder,[vim.ClusterComputeResource],True)
    children = containerView.view
    for child in children:
      configurationEx = child.configurationEx
      groups = configurationEx.group
      for group in groups:
         print("\tGroup name : "+group.name)
         if hasattr(group, 'vm'):
            print("\t\tVMs in the group :")
            for vm in group.vm:
               print("\t\t"+vm.name)
         else:
            hasattr(group, 'host')
            print("\t\tHosts in the group :")
            for host in group.host:
               print("\t\t"+host.name)

def GetDataStores(content):
    print("Getting Datastores ...")
    containerView = content.viewManager.CreateContainerView(content.rootFolder,[vim.Datacenter],True)
    print("\t Name,\tSie(GB),\tUsed(GB),\tFree(GB),\tStatus,")
    children = containerView.view
    for child in children:
      datastores = child.datastore
      if len(datastores) == 0:
             print('No Datastores',)
      else:
         for datastore in datastores:
            Name = datastore.name
            Size = (datastore.summary.capacity /1024 /1024 /1024)
            Used = ((datastore.summary.capacity /1024 /1024 /1024) - (datastore.summary.freeSpace /1024 /1024 /1024))
            Free = (datastore.summary.freeSpace /1024 /1024 /1024)
            Stat = datastore.overallStatus
            print("\t",Name+",\t"+str(Size)+",\t"+str(Used)+",\t"+str(Free)+",\t"+Stat)
            if hasattr(datastore, 'host'):
                print("\t\tHosts mounted :")
                for host in datastore.host:
                   print("\t\t"+host.key.name)
            if hasattr(datastore, 'vm'):
                print("\t\tVMs mounted :")
                for vm in datastore.vm:
                   print("\t\t"+vm.name)
            else:
                 print("\t\tNot mounted :")

def main():
   """
   Simple command-line program for listing the virtual machines on a system.
   """
   args = GetArgs()
   if args.password:
      password = args.password
   else:
      password = getpass.getpass(prompt='Enter password for host %s and '
                                        'user %s: ' % (args.host,args.user))
   context = None
   if hasattr(ssl, '_create_unverified_context'):
      context = ssl._create_unverified_context()
   si = SmartConnect(host=args.host,
                     user=args.user,
                     pwd=password,
                     port=int(args.port),
                     sslContext=context)
   if not si:
       print("Could not connect to the specified host using specified "
             "username and password")
       return -1

   atexit.register(Disconnect, si)

   content = si.RetrieveContent() 
   GetBase(si, content) 
   GetSummary(content)
   GetAlarms(content)
   GetHosts(content) 
   GetVMs(content)
   GetVMonHost(content)
   GetClusterRules(content)
   GetClusterGroups(content)
   GetDataStores(content)
   return 0

# Start program
if __name__ == "__main__":
   main()