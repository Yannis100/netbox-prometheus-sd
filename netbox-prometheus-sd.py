#!/usr/bin/env python3

import sys
import os
import json
import argparse
import itertools
import netaddr

import pynetbox


def main(args):
    targets = []
    netbox = pynetbox.api(args.url, token=args.token)

    # Filter out devices without primary IP address as it is a requirement
    # to be polled by Prometheus
    devices = netbox.dcim.devices.filter(has_primary_ip=True)
#    vm = netbox.virtualization.virtual_machines.filter(has_primary_ip=True)
    ips = netbox.ipam.ip_addresses.filter(**{'cf_%s' % args.custom_field: '{'})

    for device in itertools.chain(devices, vm, ips):
        if device.custom_fields.get(args.custom_field):
            labels = {'__port__': str(args.port)}
            if getattr(device, 'name', None):
                labels['__meta_netbox_name'] = device.name
            else:
                labels['__meta_netbox_name'] = repr(device)
            if device.tenant:
                labels['__meta_netbox_tenant'] = device.tenant.slug
                if device.tenant.group:
                    labels['__meta_netbox_tenant_group'] = device.tenant.group.slug
            if getattr(device, 'cluster', None):
                labels['__meta_netbox_cluster'] = device.cluster.name
            if getattr(device, 'asset_tag', None):
                labels['__meta_netbox_asset_tag'] = device.asset_tag
            if getattr(device, 'device_role', None):
                labels['__meta_netbox_role'] = device.device_role.slug
            if getattr(device, 'device_type', None):
                labels['__meta_netbox_type'] = device.device_type.model
            if getattr(device, 'rack', None):
                labels['__meta_netbox_rack'] = device.rack.name
            if getattr(device, 'site', None):
                labels['__meta_netbox_site'] = device.site.slug
            if getattr(device, 'serial', None):
                labels['__meta_netbox_serial'] = device.serial
            if getattr(device, 'parent_device', None):
                labels['__meta_netbox_parent'] = device.parent_device.name
            if getattr(device, 'address', None):
                labels['__meta_netbox_address'] = device.address
            if getattr(device, 'description', None):
                labels['__meta_netbox_description'] = device.description
            try:
                device_targets = json.loads(device.custom_fields[args.custom_field])
            except ValueError:
                continue  # Ignore errors while decoding the target json FIXME: logging

            # if args.tenant:
                # #filter on tenant
            # if args.device_role and args.device_type:
                # #type & role
            # elif args.device_role:
                # #role
            # elif args.device_type:
                # #type
            # else:
                # #none
            # if args.virtual-chassis:
                # #get only master device
            # if args.multi-site:
                # #multi job per site (exporter+site_name)
# #            if args.exporter
            
            if not isinstance(device_targets, list):
                device_targets = [device_targets]

            for target in device_targets:
                target_labels = labels.copy()
                target_labels.update(target)
                if hasattr(device, 'primary_ip'):
                    address = device.primary_ip
                else:
                    address = device
                targets.append({'targets': ['%s:%s' % (str(netaddr.IPNetwork(address.address).ip),
                                                       target_labels['__port__'])],
                                'labels': target_labels})

    temp_file = None
    if args.output == '-':
        output = sys.stdout
    else:
        temp_file = '{}.tmp'.format(args.output)
        output = open(temp_file, 'w')

    json.dump(targets, output, indent=4)
    output.write('\n')

    if temp_file:
        output.close()
        os.rename(temp_file, args.output)
    else:
        output.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate Prometheus config file with devices from Netbox")
    parser.add_argument('-p', '--port', default=443,
                        help='Default target port; Can be overridden using the __port__ label')
    parser.add_argument('-f', '--custom-field', default='prom_labels',
                        help='Netbox custom field to use to get the target labels')
    parser.add_argument('-t', '--tenant', default='network',
                        help='Filter devices based on tenant')
    parser.add_argument('-o', '--device_role', action="store_true",
                        help='Change snmp_exporter module to device_role slug name')
    parser.add_argument('-y', '--device_type', action="store_true",
                        help='Change snmp_exporter module to device_type slug name')
    parser.add_argument('-v', '--virtual-chassis', action="store_true",
                        help='Get only master device of Virtual-Chassis devices')
    parser.add_argument('-r', '--region', action="store_true",
                        help='Get only master device of Virtual-Chassis devices')
    parser.add_argument('-s', '--multi-site', action="store_true",
                        help='Prometheus _target_label_ to specific snmp exporter per site (multiple output.json with site names)')
    parser.add_argument('-e', '--exporter', default='exporter',
                        help='IP/FQDN (partial) name of SNMP exporter for Prometheus _target_label_ (multiple prometheus.yaml jobs with site names). \
                        By default, the site name is added at the end (if -s selected) but can be positioned with $site; $region can be used too')
    parser.add_argument('-n', '--field_site_name', default='site.name',
                        help='custom field for site name (e.g. trigram)')
    #group = parser.add_mutually_exclusive_group()
    #group.add_argument("-v", "--verbose", action="store_true")
    #group.add_argument("-q", "--quiet", action="store_true")
# We should be able to specify an exporter name containing vars from Netbox device, e.g. region : blackbox-$region-$site
    parser.add_argument('url', help='URL to Netbox')
    parser.add_argument('token', help='Authentication Token')
    parser.add_argument('output', help='Output path')

    args = parser.parse_args()
    main(args)
