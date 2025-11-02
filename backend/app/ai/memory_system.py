#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Project Starter Pro 2  —  Unified AI Memory System
Layered spatial-graph memory with FAISS vector search,
SQLite metadata, Pandas archives, and Meaning Preservation Protocol.
"""

import os, re, json, math, time, sqlite3, hashlib
from collections import Counter
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import numpy as np
import pandas as pd
import faiss


# ───────────────────────────── CONFIG ─────────────────────────────
CFG_DEFAULT = dict(
    dims=768,
    st_cap=50_000,
    mt_cap=200_000,
    age_mt_days=14,
    cold_days=30,
    theta_st=0.35,
    theta_mt=0.25,
    root="memstore"
)

COS_SIM_MIN = 0.93
ENTITY_RECALL_MIN = 0.95
SHIFT_MAX = 0.07
RATIO_MAX_BY_TIER = {"ST→MT": 0.6, "MT→LT": 0.7}


# ───────────────────────────── UTILITIES ─────────────────────────────
def now() -> float: return time.time()
def sha256(s: str) -> str: return hashlib.sha256(s.encode()).hexdigest()
def clamp(x, a, b): return a if x < a else b if x > b else x
def l2(v): return math.sqrt(sum(x*x for x in v))
def dot(a,b): return float(np.dot(a,b))
def cosine(a,b):
    na, nb = l2(a), l2(b)
    return 0 if na==0 or nb==0 else dot(a,b)/(na*nb)

_rx_word = re.compile(r"[A-Za-z0-9_]+")
def tokenize(text:str)->List[str]: return [w.lower() for w in _rx_word.findall(text)]

def embed(text:str,dims:int)->np.ndarray:
    """Lightweight hashing embedding"""
    vec = np.zeros(dims, dtype=np.float32)
    for tok,c in Counter(tokenize(text)).items():
        h=int(hashlib.md5(tok.encode()).hexdigest(),16)
        idx=h%dims
        sign=1 if (h>>1)&1 else -1
        vec[idx]+=sign*(1+math.log1p(c))
    n=l2(vec)
    return vec/n if n>0 else vec


# ───────────────────────────── FAISS INDEX ─────────────────────────────
class FaissIndex:
    def __init__(self, path:str, dims:int):
        self.path = path
        self.dims = dims
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.index = faiss.IndexFlatIP(dims)
        self.ids: List[str] = []
        self.meta: Dict[str,dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path+".faiss"):
            self.index = faiss.read_index(self.path+".faiss")
        if os.path.exists(self.path+".meta.json"):
            with open(self.path+".meta.json") as f: self.meta=json.load(f)
        self.ids=list(self.meta.keys())

    def save(self):
        faiss.write_index(self.index, self.path+".faiss")
        with open(self.path+".meta.json","w") as f: json.dump(self.meta,f)

    def add(self, rid:str, emb:np.ndarray, meta:dict):
        v=np.expand_dims(emb.astype("float32"),0)
        self.index.add(v)
        self.ids.append(rid)
        self.meta[rid]=meta

    def topk(self, emb:np.ndarray, k:int=20)->List[Tuple[str,float]]:
        if not self.ids: return []
        q=np.expand_dims(emb.astype("float32"),0)
        D,I=self.index.search(q,k)
        return [(self.ids[i], float(D[0][j])) for j,i in enumerate(I[0]) if i<len(self.ids)]


# ───────────────────────────── DB HELPERS ─────────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS heads(
 id TEXT PRIMARY KEY, ts REAL, tier TEXT, title TEXT,
 summary_core TEXT, summary_text TEXT,
 emb BLOB, sets TEXT, meta TEXT,
 recency REAL, freq REAL, utility REAL, novelty REAL,
 pin INTEGER, size INTEGER, body_ptr TEXT, mpp TEXT);
CREATE INDEX IF NOT EXISTS idx_tier ON heads(tier);
CREATE INDEX IF NOT EXISTS idx_ts ON heads(ts);
"""

def ensure_db(path:str):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    c=sqlite3.connect(path)
    c.executescript(DDL); c.commit()
    return c


# ───────────────────────────── MEANING PRESERVATION ─────────────────────────────
def extract_entities(text:str)->List[str]:
    ents=re.findall(r"[A-Z][A-Za-z0-9_\-]{2,}",text)
    return list(dict.fromkeys(ents))

def extractive_summary(text:str,ratio:float)->str:
    sents=re.split(r'(?<=[.!?])\s+',text)
    if len(sents)<=1: return text
    tf=Counter(tokenize(text))
    scored=[(sum(tf[t] for t in tokenize(s))/max(1,len(s)),s) for s in sents]
    scored.sort(reverse=True,key=lambda x:x[0])
    k=max(1,int(len(sents)*ratio))
    return " ".join(s for _,s in scored[:k])

def abstractive_trim(text:str,ratio:float)->str:
    w=text.split(); return " ".join(w[:max(1,int(len(w)*ratio))])

def summarize_with_mpp(body:str,meta:dict,tier:str,dims:int)->Dict:
    ents=extract_entities(body)
    e_full=embed(body,dims)
    ratio=min(RATIO_MAX_BY_TIER.get(tier,0.7),0.6)
    summ=abstractive_trim(extractive_summary(body,ratio),ratio)
    e_sum=embed(summ,dims)
    cos=cosine(e_full,e_sum)
    shift=float(np.linalg.norm(e_full-e_sum))
    ent_recall=len(set(ents)&set(extract_entities(summ)))/max(1,len(ents))
    if cos<COS_SIM_MIN or ent_recall<ENTITY_RECALL_MIN or shift>SHIFT_MAX:
        raise RuntimeError("meaning-loss")
    return {
        "summary_core":"; ".join(ents[:50]),
        "summary_text":summ,
        "trace":{
            "cos":cos,"ent_recall":ent_recall,"shift":shift,
            "created":now(),"model":"mpp-rule"
        }
    }


# ───────────────────────────── TIER ─────────────────────────────
class Tier:
    def __init__(self,name:str,root:str,dims:int):
        self.name=name
        self.db=ensure_db(f"{root}/{name}.sqlite")
        self.fi=FaissIndex(f"{root}/{name}",dims)

    def upsert(self,h:dict):
        self.db.execute("""REPLACE INTO heads
            (id,ts,tier,title,summary_core,summary_text,emb,sets,meta,
             recency,freq,utility,novelty,pin,size,body_ptr,mpp)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (h["id"],h["ts"],h["tier"],h["title"],h["core"],h["sum"],
             h["emb"].tobytes(),json.dumps(h["sets"]),json.dumps(h["meta"]),
             *[h["scores"][k] for k in ("recency","freq","utility","novelty")],
             int(h["scores"]["pin"]),h["scores"]["size"],h["ptr"],json.dumps(h.get("mpp",{}))))
        self.db.commit()
        self.fi.add(h["id"],h["emb"],{"tier":self.name})
        self.fi.save()

    def fetch(self,rid:str)->Optional[dict]:
        row=self.db.execute("SELECT id,summary_text,body_ptr,meta,mpp FROM heads WHERE id=?",(rid,)).fetchone()
        if not row: return None
        return dict(id=row[0],summary=row[1],ptr=row[2],meta=json.loads(row[3]),mpp=json.loads(row[4]))

    def topk(self,emb:np.ndarray,k:int)->List[Tuple[str,float]]:
        return self.fi.topk(emb,k)


# ───────────────────────────── SYSTEM CORE ─────────────────────────────
class MemorySystem:
    def __init__(self,cfg:dict|None=None):
        self.cfg=CFG_DEFAULT| (cfg or {})
        r=self.cfg["root"]; d=self.cfg["dims"]
        os.makedirs(r,exist_ok=True)
        self.tiers={n:Tier(n,r,d) for n in ("st","mt","lt_hot","fv")}
        self.arch=os.path.join(r,"arch")
        os.makedirs(self.arch,exist_ok=True)

    def _write_body(self,text:str,rid:str)->str:
        y,m=time.strftime("%Y"),time.strftime("%m")
        p=Path(self.arch)/y/m; p.mkdir(parents=True,exist_ok=True)
        f=p/f"part-{time.strftime('%d')}.jsonl"
        with open(f,"a") as fh: fh.write(json.dumps({"id":rid,"body":text})+"\n")
        return str(f)

    def insert(self,text:str,sets=None,meta=None,pin=False,title="")->str:
        sets,meta=sets or [],meta or {}
        rid=sha256(text+str(now()))[:16]
        emb=embed(text,self.cfg["dims"])
        ptr=self._write_body(text,rid)
        h=dict(id=rid,ts=now(),tier="ST",title=title,core="",sum="",
               emb=emb,sets=sets,meta=meta,
               scores=dict(recency=1,freq=0,utility=meta.get("utility",0.5),
                           novelty=0.5,pin=pin,size=len(text)),
               ptr=ptr)
        self.tiers["st"].upsert(h)
        return rid

    def teach(self,text:str,sets=None,title="")->str:
        rid=self.insert(text,sets,{"utility":0.9},True,title)
        h=self.tiers["st"].fetch(rid)
        try:
            mpp=summarize_with_mpp(text,{"utility":0.9},"ST→MT",self.cfg["dims"])
            h.update(core=mpp["summary_core"],sum=mpp["summary_text"],mpp=mpp["trace"])
            h.update(emb=embed(text,self.cfg["dims"]),tier="FV",
                     sets=sets or [],meta={"src":"teach"},
                     scores=dict(recency=1,freq=1,utility=0.9,novelty=0.3,pin=True,size=len(text)),ptr=h["ptr"])
            self.tiers["fv"].upsert(h)
        except Exception as e:
            print("MPP fail",e)
        return rid

    def recall(self,query:str,k:int=10,sets_filter=None)->List[dict]:
        qemb=embed(query,self.cfg["dims"])
        cands=[]
        for n,t in self.tiers.items():
            for rid,score in t.topk(qemb,k):
                cands.append((rid,score,n))
        cands.sort(key=lambda x:x[1],reverse=True)
        out=[]
        seen=set()
        for rid,sc,tier in cands:
            if rid in seen: continue
            seen.add(rid)
            h=self.tiers[tier].fetch(rid)
            if not h: continue
            out.append(dict(id=rid,score=round(sc,3),tier=tier,summary=h["summary"],mpp=h["mpp"]))
            if len(out)>=k: break
        return out

    def load(self) -> None:
        """Load/reload on-disk indices and metadata for all tiers.
        Safe no-op if already loaded.
        """
        for name, t in self.tiers.items():
            try:
                # Re-read FAISS + metadata from disk
                t.fi._load()  # private but stable in our implementation
            except Exception as e:
                print(f"memory.load warn ({name}): {e}")

    def retrieve_context(self, query: str, k: int = 10, project: Optional[str] = None, category: Optional[str] = None) -> List[dict]:
        """Recall from global memory and (optionally) the per-project RAG store.
        Returns a unified, score-normalized list of context items.
        """
        mem = self.recall(query, k=k)
        rag = []
        if project:
            try:
                from backend.app.ai.memory_adapter import UnifiedMemoryAdapter
                adapter = UnifiedMemoryAdapter(project)
                rag = adapter.search(query, k=k, category=category) or []
            except Exception as e:
                print(f"memory.retrieve_context: rag error: {e}")

        def to_item(x: dict, source: str) -> dict:
            rid = x.get("id") or x.get("point_id") or x.get("uuid") or sha256(json.dumps(x))[:16]
            score = float(x.get("score", 0.0))
            title = x.get("title") or (x.get("metadata", {}) or {}).get("title") or ""
            summary = x.get("summary") or x.get("text") or (x.get("metadata", {}) or {}).get("text") or ""
            tier = x.get("tier") or ""
            cat_val = x.get("category") or (x.get("metadata", {}) or {}).get("category") or (category or "")
            return {"id": rid, "score": score, "title": title, "summary": summary, "tier": tier, "category": cat_val, "source": source}

        items = [to_item(x, "memory") for x in mem] + [to_item(x, "rag") for x in rag]

        # Normalize scores within each source to [0,1] to make merging fair
        for src in ("memory", "rag"):
            vals = [it["score"] for it in items if it["source"] == src]
            if len(vals) >= 2:
                mn, mx = min(vals), max(vals)
                rng = (mx - mn) or 1.0
                for it in items:
                    if it["source"] == src:
                        it["score"] = (it["score"] - mn) / rng

        items.sort(key=lambda d: d["score"], reverse=True)
        return items[:k]

    def store_interaction(self, agent_name: str, query: str, response: str, project: Optional[str] = None) -> str:
        """Store a chat interaction in the unified memory and mirror into the
        project's RAG (if a project is provided).
        """
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        text = (
            f"[interaction]\nagent={agent_name}\ntime={ts}\n\n[query]\n{query}\n\n[response]\n{response}\n"
        )
        sets = [f"agent:{agent_name}", "interaction"]
        if project:
            sets.append(f"project:{project}")
        rid = self.insert(
            text,
            sets=sets,
            meta={"type": "chat_interaction", "project": project or ""},
            title=f"Chat with {agent_name}"
        )
        if project:
            try:
                from backend.app.ai.memory_adapter import UnifiedMemoryAdapter
                adapter = UnifiedMemoryAdapter(project)
                adapter.add_text(
                    response,
                    title=f"Chat: {agent_name}",
                    category="docs",
                    meta={"source": "interaction", "agent": agent_name},
                )
            except Exception as e:
                print(f"memory.store_interaction: rag mirror error: {e}")
        return rid


    def tick(self):
        st=self.tiers["st"]
        rows=st.db.execute("SELECT id,body_ptr,meta FROM heads").fetchall()
        for rid,ptr,meta_s in rows:
            try:
                df=pd.read_json(ptr,lines=True)
                body=df.loc[df["id"]==rid,"body"].values[0]
                meta=json.loads(meta_s)
                mpp=summarize_with_mpp(body,meta,"ST→MT",self.cfg["dims"])
                h=dict(id=rid,ts=now(),tier="MT",title="",
                       core=mpp["summary_core"],sum=mpp["summary_text"],emb=embed(body,self.cfg["dims"]),
                       sets=[],meta=meta,
                       scores=dict(recency=0.8,freq=0.2,utility=meta.get("utility",0.5),
                                   novelty=0.4,pin=False,size=len(body)),
                       ptr=ptr,mpp=mpp["trace"])
                self.tiers["mt"].upsert(h)
                st.db.execute("DELETE FROM heads WHERE id=?",(rid,))
            except Exception as e:
                print("tick fail",e)
        st.db.commit()

    def validate(self,rid:str)->bool:
        for t in self.tiers.values():
            h=t.fetch(rid)
            if not h: continue
            df=pd.read_json(h["ptr"],lines=True)
            body=df.loc[df["id"]==rid,"body"].values[0]
            ef,es=embed(body,self.cfg["dims"]),embed(h["summary"],self.cfg["dims"])
            cos,shift=cosine(ef,es),float(np.linalg.norm(ef-es))
            return cos>=COS_SIM_MIN and shift<=SHIFT_MAX
        return False


# Singleton instance
memory_system = MemorySystem()

