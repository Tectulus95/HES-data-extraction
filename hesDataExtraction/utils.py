import mgrs

m = mgrs.MGRS()

def makedict(columns:list[str], entries:list[str]) -> dict:
    """Turns a line of the HES data into a dictionary
    
    Parameters
    ----------
    columns : list[str]
        Previously extracted column names
    entries : list[str]
        Entries in given line

    Returns
    -------
    dict
    """
    entrydict = {}
    for i, column in enumerate(columns):
        entrydict[column] = entries[i]
    return(entrydict)

def toCoord(mgrs: str) -> tuple:
    """Turns the entered mgrs coordinates into LatLon coordinates
    Grid zone designator has to be ascertained by trial and error

    Parameters
    ----------
    mgrs: str
        mgrs as given in HES data without the grid zone designator

    Returns
    -------
    tuple
        latitude and longitude
    """
    try:
        d = m.toLatLon(('48P'+mgrs))
    except:
        try:
            d = m.toLatLon(('48Q'+mgrs))
        except:
            try:
                d = m.toLatLon(('49P'+mgrs))
            except:
                try:
                    d = m.toLatLon(('49Q'+mgrs))
                except:
                    d = None
    return d

def progress(task: str, current: int, total: int) -> None:
    """Prints a simple progress indicator for monitoring purposes

    Parameters
    ----------
    task: str
        Short description of the current task
    current: int
        Current iteration
    total: int
        Total number of iterations
    """
    percentage = (current+1)/total*100
    if current+1 == total:
        print(f"{task}: {percentage:.1f}%")
    else:
        print(f"{task}: {percentage:.1f}%", end="\r")