"""Independent linear oracle. No imports from the optimizer or sandbox."""

def independent_choice(request):
    best=None
    for offer in request['offers']:
        candidate={
            'supplier_id':str(offer['supplier_id']).strip(),
            'product':str(offer['product']).strip(),
            'available_qty':int(offer['available_qty']),
            'total_cost':float(offer['total_cost']),
            'eta_days':int(offer['eta_days']),
        }
        if candidate['product']!=str(request['product']).strip(): continue
        if candidate['available_qty']<int(request['quantity']): continue
        if candidate['total_cost']>float(request['max_budget']): continue
        if candidate['eta_days']>int(request['deadline_days']): continue
        if best is None:
            best=candidate
        elif candidate['total_cost']<best['total_cost']:
            best=candidate
        elif candidate['total_cost']==best['total_cost']:
            if candidate['eta_days']<best['eta_days']:
                best=candidate
            elif candidate['eta_days']==best['eta_days'] and candidate['supplier_id']<best['supplier_id']:
                best=candidate
    return best
