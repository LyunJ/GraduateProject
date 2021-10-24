import json

def IP(path,selector): 
    with open(f'{path}/ips.json','r') as f:
        ip_data = json.load(f)
        kafka = ip_data['kafka']
        mongo = ip_data['mongo']
    
    if selector == 'kafka':
        return kafka
    if selector == 'mongo':
        return mongo