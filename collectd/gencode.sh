#!/bin/bash
cd protocol && thrift --gen py -out genpy collectd.thrift
