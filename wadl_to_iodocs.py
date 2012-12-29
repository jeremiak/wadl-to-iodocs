#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
import re
import simplejson as json
import sys

def wadl_to_rails_syntax(url):
    url = re.sub(r'{', r':', url)
    url = re.sub(r'}', r'', url)
    
    print url
    
    return url

def params_to_json(params):
    param_list = []
    for param in params:
        p = {
                'Name': param['name'],
                'Required': 'Y' if param['required'] == 'true' else 'N',
                'Default': '',
                'Type': 'string' if param['type'] == 'xsd:string' else param['type'],
                'Description': ''
            }
        try:
            p['Description'] = param.doc.text
        except AttributeError:
            p['Description'] = ''
        
        param_list.append(p)

    return param_list

def method_to_json(method):
    j = {
            'MethodName': method['apigee:displayname'],
            'Synopsis': method.doc.text,
            'HTTPMethod': method['name'],
            'URI': '',
            'RequiresOAuth': 'N',
            'parameters': [],
        }

    print method.request
    params = method.request.findAll('param')
    
    print len(params)

    p = params_to_json(params)
    j['parameters'] = p

    return j

if __name__=='__main__':
    wf = sys.argv[1]
    jf = sys.argv[2]
    
    print wf
    print jf
    
    wadl_file = open('%s' % wf)
    json_file = open('%s' % jf, 'w+')

    soup = BeautifulSoup(wadl_file.read())

    print soup

    resources = soup.findAll('resource')

    groups = {}
    tags = soup.findAll('apigee:tag', primary='true')
    for tag in tags:
        p = tag.text
        if p not in groups.keys():
            groups[p] = []
        else:
            pass

    for resource in resources:
        methods = resource.findAll('method')
        for method in methods:
            print method['apigee:displayname']
            j = method_to_json(method)
            j['URI'] = wadl_to_rails_syntax(resource['path'])
            group = method.findAll('apigee:tag', primary='true')[0].text
            groups[group].append(j)

    endpoints = []
    for key in groups:
        key_str = '%s related methods' % key
        
        endpoints.append({'name': key_str, 'methods': groups[key]})
        
    data = json.dumps({'endpoints': endpoints }, sort_keys=True, indent=4)
    json_file.write(data)
