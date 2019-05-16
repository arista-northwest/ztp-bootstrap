#!/usr/bin/env python
# Copyright (c) 2015 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import eossdk
from subprocess import check_output, CalledProcessError
import sys
import time

class ZtpsInterfaceMonitor(eossdk.AgentHandler, eossdk.IntfHandler):
   def __init__(self, intfMgr, agentMgr):
      eossdk.AgentHandler.__init__(self, agentMgr)
      eossdk.IntfHandler.__init__(self, intfMgr)
      self.tracer = eossdk.Tracer("ZtpsInterfaceMonitor")
      self.intfMgr_ = intfMgr
      self.agentMgr_ = agentMgr

      self.dhcpdRestarts_ = 0
      self.dhcpdRestartsFailed_ = 0

   def on_initialized(self):
      self.watch_all_intfs(True)
      self.agentMgr_.status_set("DHCPD restarts", "0")

   def on_oper_status(self, intfId, operState):
      if operState == eossdk.INTF_OPER_UP:
          try:
              output = check_output(["sudo", "service", "dhcpd", "restart"])
              self.dhcpdRestarts_ += 1
              self.agentMgr_.status_set("DHCPD restarts", str(self.dhcpdRestarts_))
          except CalledProcessError as exc:
              self.dhcpdRestartsFailed_ += 1
              self.agentMgr_.status_set("DHCPD restarts failed", str(self.dhcpdRestartsFailed_))
              self.agentMgr_.status_set("Last failed msg", str(exc))


if __name__ == "__main__":
   sdk = eossdk.Sdk()
   _ = ZtpsInterfaceMonitor(sdk.get_intf_mgr(), sdk.get_agent_mgr())
   sdk.main_loop(sys.argv)
