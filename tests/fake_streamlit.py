"""A tiny fake of the Streamlit API, enough to execute LunaBase's app.py top to bottom and catch runtime errors.

Tests use it because the real Streamlit server cannot always be started (CI / offline). It is NOT a substitute for
one manual run of `streamlit run app.py` on the target device."""
import sys, types, collections.abc

class StopScript(Exception): pass
class Rerun(Exception): pass

class SS(dict):
    __getattr__=lambda s,k: s[k] if k in s else (_ for _ in ()).throw(AttributeError(k))
    def __setattr__(s,k,v): s[k]=v
    def __delattr__(s,k): del s[k]

class Dummy:
    def __enter__(s): return s
    def __exit__(s,*a): return False
    def __call__(s,*a,**k): return Dummy()
    def __getattr__(s,n):
        if n.startswith('__'): raise AttributeError(n)
        return Dummy()
    def __bool__(s): return False
    def __iter__(s): return iter([Dummy(),Dummy(),Dummy(),Dummy()])
    def __str__(s): return ''

CALLS=collections.defaultdict(list)
CLICK=set()            # button keys that return True on the next run
state=SS()
COMPONENT={'value':None,'last_kwargs':None}

def _rec(name):
    def f(*a,**k): CALLS[name].append((a,k)); return Dummy()
    return f

def button(label,key=None,**k):
    CALLS['button'].append((label,key,k))
    if key in CLICK: CLICK.discard(key); return True
    return False
def text_input(label,value="",key=None,**k):
    if key is not None:
        if key not in state: state[key]=value
        return state[key]
    return value
def selectbox(label,options,index=0,key=None,**k):
    options=list(options)
    if key is not None:
        if key not in state: state[key]=options[index] if index is not None else None
        return state[key]
    return options[index] if index is not None else None
def segmented_control(label,options,key=None,**k):
    return state.get(key)
def radio(label,options,index=0,key=None,**k):
    options=list(options)
    if key is not None:
        if key not in state: state[key]=(options[index] if index is not None else None)
        return state[key]
    return options[index] if index is not None else None
def checkbox(label,value=False,key=None,**k):
    if key is not None:
        if key not in state: state[key]=value
        return state[key]
    return value
def slider(label,mn,mx,value=None,key=None,**k):
    if key is not None:
        if key not in state: state[key]=value
        return state[key]
    return value
class Col(Dummy):
    def button(s,*a,**k): return button(*a,**k)
    def selectbox(s,*a,**k): return selectbox(*a,**k)
    def metric(s,*a,**k): CALLS['metric'].append((a,k))
def columns(spec,**k):
    n=spec if isinstance(spec,int) else len(spec)
    return [Col() for _ in range(n)]
def stop(): raise StopScript()
def rerun(): raise Rerun()
def cache_data(*a,**k):
    if a and callable(a[0]): return a[0]
    return lambda f:f
def dialog(*a,**k): return lambda f:f
def container(*a,**k): return Dummy()
def expander(*a,**k): return Dummy()
def form(*a,**k): return Dummy()
def tabs(labels): return [Dummy() for _ in labels]
def metric(*a,**k): CALLS['metric'].append((a,k))
def download_button(*a,**k): CALLS['download'].append((a,k)); return False

st=types.ModuleType('streamlit')
st.session_state=state
for n,f in dict(button=button,text_input=text_input,selectbox=selectbox,segmented_control=segmented_control,radio=radio,
                checkbox=checkbox,slider=slider,columns=columns,stop=stop,rerun=rerun,cache_data=cache_data,dialog=dialog,
                container=container,expander=expander,form=form,tabs=tabs,download_button=download_button).items():
    setattr(st,n,f)
for n in ('markdown','write','caption','info','success','warning','error','toast','balloons','progress','line_chart','bar_chart',
          'scatter_chart','dataframe','divider','set_page_config','subheader','header','text','code','json','metric','title','html'):
    setattr(st,n,_rec(n))
def _ga(n):
    if n.startswith('__'): raise AttributeError(n)
    return Dummy()
st.__getattr__=_ga

comp=types.ModuleType('streamlit.components.v1')
def declare_component(name,path=None,**k):
    def call(**kw):
        COMPONENT['last_kwargs']=kw; return COMPONENT['value']
    return call
comp.declare_component=declare_component
comp.html=_rec('components.html')
cpk=types.ModuleType('streamlit.components'); cpk.v1=comp
st.components=cpk
MODULES={'streamlit':st,'streamlit.components':cpk,'streamlit.components.v1':comp}


def install():
    """Put the fake in sys.modules; returns the previous entries so the caller can restore them."""
    old={k:sys.modules.get(k) for k in MODULES}
    sys.modules.update(MODULES)
    return old


def uninstall(old):
    for k,v in old.items():
        if v is None: sys.modules.pop(k,None)
        else: sys.modules[k]=v

def run_app(path, max_reruns=8):
    """Execute the script; a st.rerun() restarts it (like Streamlit does). Returns number of passes."""
    src=open(path,encoding='utf-8').read(); code=compile(src,path,'exec')
    for n in range(max_reruns):
        for m in [m for m in sys.modules if m in ('panels','theme','ui_html','scene_explorer')]:
            pass
        g={'__name__':'__main__','__file__':path}
        try:
            exec(code,g); return n+1,g
        except Rerun: continue
        except StopScript: return n+1,g
    raise RuntimeError('rerun loop')
