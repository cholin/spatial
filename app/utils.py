from datetime import datetime, date

def get_datetime(fdate = None, fhours = None):
    if fhours is None:
        ftime = datetime.min.time()
    else:
        ftime = datetime.strptime(fhours, '%H').time()

    if fdate is None:
        fdate = date.today()
    else:
        fdate = datetime.strptime(fdate, '%Y-%m-%d').date()

    
    return datetime.combine(fdate, ftime)
