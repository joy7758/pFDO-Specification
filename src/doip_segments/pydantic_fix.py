import sys
import json
import os

def replace_const(file):
    filename=os.path.basename(file)
    with open(file) as json_data:
        d = json.load(json_data)
        if d['properties'].get('operationId'):
            if d['properties']['operationId'].get('const'):
                d['properties']['operationId']['enum']=[d['properties']['operationId']['const']]
                del d['properties']['operationId']['const']

        elif d['properties'].get('status'):
            if d['properties']['status'].get('const'):
                d['properties']['status']['enum'] = [d['properties']['status']['const']]
                del d['properties']['status']['const']
        else:
            print("noting to do")
    with open(filename, 'w') as fp:
        json.dump(d, fp)
if __name__ == "__main__":
    replace_const(sys.argv[1])