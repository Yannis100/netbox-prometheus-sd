Service discovery for [Prometheus](https://prometheus.io/) using devices from [Netbox](https://github.com/digitalocean/netbox).

# Legal

This project is released under MIT license, copyright 2018 ENIX SAS.

# Contribute

Feel free to contribute to this project through Github pull-requests. We also
accept well formatted git patches sent by email to the maintainer.

Current Maintainer: Antoine Millet <antoine.millet __at__ enix.io>

# Requirement

This project requires Python 3 and [Pynetbox](https://github.com/digitalocean/pynetbox/).

Also, this project requires a custom field to be created into your Netbox instance.
By default, this custom field is named `prom_labels` and can be created in the
Netbox admin page (Home -> Extras -> Custom fields) with the following settings:

- Objects: select `dcim > device` and `virtualization > virtual machine`
- Type: `Text`
- Name: `prom_labels`

# Usage

```
usage: netbox-prometheus-sd.py [-h] [-p PORT] [-f CUSTOM_FIELD] [-t TENANT]
                               [-r] [-d] [-v] [-s] [-e EXPORTER]
                               [-n FIELD_SITE_NAME]
                               url token output

Generate Prometheus config file with devices from Netbox

positional arguments:
  url                   URL to Netbox
  token                 Authentication Token
  output                Output path

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Default target port; Can be overridden using the
                        __port__ label
  -f CUSTOM_FIELD, --custom-field CUSTOM_FIELD
                        Netbox custom field to use to get the target labels
  -t TENANT, --tenant TENANT
                        Filter devices based on tenant
  -r, --device_role     Change snmp_exporter module to device_role slug name
  -d, --device-type     Change snmp_exporter module to device_type slug name
  -v, --virtual-chassis
                        Get only master device of Virtual-Chassis devices
  -s, --multi-site      Prometheus _target_label_ to specific snmp exporter
                        per site (multiple output.json with site names)
  -e EXPORTER, --exporter EXPORTER
                        IP/FQDN (partial) name of SNMP exporter for Prometheus
                        _target_label_ (multiple prometheus.yaml jobs with
                        site names). By default, the site name is added at the
                        end (if -s selected) but can be positioned with $site;
                        $region can be used too
  -n FIELD_SITE_NAME, --field_site_name FIELD_SITE_NAME
                        IP/FQDN (partial) name of SNMP exporter for Prometheus
                        _target_label_ (multiple prometheus.yaml jobs with
```

The service discovery script requires the URL to the Netbox instance, an
API token that can be generated into the user profile page of Netbox and a path
to an output file.

Optionally, you can customize the custom field used to get target labels in Netbox
using the `--custom-field` option. You can also customize the default port on which
the target will point to using the `--port` option. Note that this port can be customized
per target using the `__port__` label set in the custom field.

The outputs will be generated in the folder pointed by the `output` argument. (`prometheus.yaml` config file with multiple jobs (`-e -s` args) and multiple `output.json` depending on `-r -d -s` arguments)

In the Prometheus configuration, declare a new scrape job using the file_sd_configs
service discovery:

```
- job_name: 'netbox'
  file_sd_configs:
  - files:
    - '/path/to/my/output.json'
```
