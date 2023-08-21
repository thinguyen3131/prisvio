import xml.dom.minidom


def find_windows_timezone_by_name(name):
    data = xml.dom.minidom.parse('windowsZones.xml')
    zones = data.getElementsByTagName('mapZone')
    for zone in zones:
        if zone.getAttribute('other') == name:
            return zone.getAttribute('type')
