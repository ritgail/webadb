import subprocess

def adb(args, device=None, adbpath='adb'):
    base = [adbpath]
    if device is not None:
        base += ['-s', device]

    args = base + args
    print(args)
    try:
        p = subprocess.Popen([str(arg) for arg in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(timeout=30)  # 30-second timeout
        return (p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8'))
    except subprocess.TimeoutExpired:
        p.kill()
        return (-1, '', 'Command timed out')
    except FileNotFoundError:
        return (-1, '', f'ADB executable not found at {adbpath}')
    except Exception as e:
        return (-1, '', f'An error occurred: {str(e)}')
    
def _getprop(device, property, default):
    (rc, out, _) = adb(['shell', 'getprop', property], device=device)
    print(rc,out,_)
    if not rc == 0:
        return default
    elif out.strip():
        return out.strip()
    else:
        return default
def get_devices():
    (_, out, _) = adb(['devices'])
    print(out)
    devices = []
    for l in out.split('\n'.encode("utf-8")):
        tokens = l.split()
        if not len(tokens) == 2:
            # Discard line that doesn't contain device information
            continue

        id = tokens[0].decode('utf-8')
        devices.append({
            'id': id,
            'manufacturer': _getprop(id, 'ro.product.manufacturer', 'unknown'),
            'model': _getprop(id, 'ro.product.model', 'unknown'),
            'sdk': _getprop(id, 'ro.build.version.sdk', 'unknown'),
            # 'network': _getnetwork(id),
            # 'battery': _getbattery(id),
            # 'screen': _getscreen(id)
        })
    print(devices)
    return devices

def _getnetwork(device):
    (rc, out, err) = adb(["shell", "dumpsys wifi | grep 'current SSID' | grep -o '{.*}'"], device=device)
    ore = out
    ore = ore.decode("utf-8")
    ore = ore.replace('=', ':')
    ore = ore.replace('iface', '"iface"')
    ore = ore.replace('"iface":', '"iface":"')
    ore = ore.replace(',ssid', '","ssid"')
    oreDict = json.loads(ore)

    print('network done ' + str(rc))
    if rc != 0:
        print(err)

    network = {
        'connected': True,
        'ssid': oreDict['ssid']
    }

    for l in out.split('\n'.encode("utf-8")):
        tokens = l.split()
        if not len(tokens) > 10 or tokens[0] != 'mNetworkInfo':
            continue
        print("Token 4:", tokens[4])
        print("Token 8:", tokens[8])
        network['connected'] = (tokens[4].startswith('CONNECTED/CONNECTED'.encode("utf-8")))
        network['ssid'] = tokens[8].replace('"'.encode("utf-8"), ''.encode("utf-8")).rstrip(','.encode("utf-8"))

    return network


if __name__ == '__main__':
    _getprop('192.168.0.20:5555','ro.product.manufacturer', 'unknown')
    _getprop('192.168.0.20:5555', 'ro.product.model', 'unknown')
    _getprop('192.168.0.20:5555', 'ro.build.version.sdk', 'unknown')
    print(adb(["shell", "dumpsys wifi | grep 'current SSID' | grep -o '{.*}'"]))
    _getnetwork('192.168.0.20:5555')