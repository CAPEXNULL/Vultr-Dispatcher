import json, sys

def violations(req, o):
    out=[]
    if str(o['product']).strip()!=str(req['product']).strip(): out.append('product')
    if int(o['available_qty'])<int(req['quantity']): out.append('quantity')
    if float(o['total_cost'])>float(req['max_budget']): out.append('budget')
    if int(o['eta_days'])>int(req['deadline_days']): out.append('deadline')
    return out

def solve(req):
    eligible=[]; conflicts={}
    for raw in req['offers']:
        o={
            'supplier_id':str(raw['supplier_id']).strip(),
            'product':str(raw['product']).strip(),
            'available_qty':int(raw['available_qty']),
            'total_cost':float(raw['total_cost']),
            'eta_days':int(raw['eta_days'])
        }
        v=violations(req,o)
        if v: conflicts[o['supplier_id']]=v
        else: eligible.append(o)
    eligible.sort(key=lambda o:(o['total_cost'],o['eta_days'],o['supplier_id']))
    selected=eligible[0] if eligible else None
    return {
        'status':'PROPOSED' if selected else 'CONFLICT',
        'eligible':eligible,
        'selected':selected,
        'conflicts':conflicts,
        'objective':{'type':'lexicographic','priority':['total_cost','eta_days','supplier_id']}
    }

if __name__=='__main__':
    input_path, output_path = sys.argv[1], sys.argv[2]
    with open(input_path,'r',encoding='utf-8') as f: req=json.load(f)
    result=solve(req)
    with open(output_path,'w',encoding='utf-8') as f: json.dump(result,f,sort_keys=True)
