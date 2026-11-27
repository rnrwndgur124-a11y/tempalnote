"""페이지마다 공유 미리보기 이미지(1200x630 jpg)를 만든다: 게임 화면 + 페이지 제목."""
import re, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0,'/home/claude/tempal')
src=open('/home/claude/tempal/index.html',encoding='utf-8').read()
PAGES={}
for m in re.finditer(r"\b([a-z]+):\{t:'([^']+)',d:'([^']+)'",src): PAGES.setdefault(m.group(1),(m.group(2),m.group(3)))
PAGES['home']=('템빨 오버기어드 팬 도구 모음','강화 계산기 · 숙제 · 제작 도감 · 쿠폰 · 방송인 서버')
IMG={'growth':'overgeared','collect':'feat-codex','drops':'feat-map','hidden':'feat-archive','gear':'enhsup','outfit':'feat-outfit','home':'art','quiz':'select','enhance':'enhsup','calc':'enhsup','godhand':'ghsum','homework':'mission8','starter':'select','weapons':'feat-wpn','systems':'overgeared','roadmap':'art','bm':'launchpk','coupons':'attend','pets':'feat-pet','timer':'quest','backup':'art','videos':'art','official':'art','contact':'art','privacy':'art','terms':'art','about':'art','news':'attend','trade':'exchange','streamers':'fight1','community':'art','prob':'feat-prob','archive':'feat-archive','map':'feat-map','hunt':'feat-map','codex':'feat-codex','sim':'feat-sim','craft':'craft','titles':'titles','achieve':'achieve'}
F='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FM='/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc'
def font(p,s): return ImageFont.truetype(p,s,index=1)
def wrap(d,t,f,w):
    lines=[];cur=''
    for ch in t:
        if d.textlength(cur+ch,font=f)>w and cur:
            cut=cur.rfind(' ');
            if cut>len(cur)*0.5: lines.append(cur[:cut]); cur=cur[cut+1:]+ch
            else: lines.append(cur); cur=ch
        else: cur+=ch
    if cur: lines.append(cur)
    return lines
DIRECT={'streamers','community'}  # 직접 디자인한 공유 이미지 사용 (gfx/*.html)
for k,(t,d) in PAGES.items():
    if k not in IMG or k in DIRECT: continue
    bg=Image.open(f'/home/claude/site/img/ui/{IMG[k]}.webp').convert('RGB')
    r=max(1200/bg.width,630/bg.height); bg=bg.resize((int(bg.width*r)+1,int(bg.height*r)+1),Image.LANCZOS)
    x=(bg.width-1200)//2; y=(bg.height-630)//2; bg=bg.crop((x,y,x+1200,y+630))
    # 왼쪽이 어두운 그라데이션
    g=Image.new('L',(1200,1)); [g.putpixel((i,0),int(235-170*min(1,i/900))) for i in range(1200)]
    g=g.resize((1200,630)); dark=Image.new('RGB',(1200,630),(5,10,20)); bg=Image.composite(dark,bg,g)
    dr=ImageDraw.Draw(bg)
    dr.rectangle((0,0,1200,6),fill=(201,162,74))
    dr.text((64,58),'템빨 : 대장간노트',font=font(F,34),fill=(227,194,122))
    ft=font(F,68); ls=wrap(dr,t,ft,820)[:3]; yy=150
    for l in ls: dr.text((64,yy),l,font=ft,fill=(255,255,255)); yy+=86
    fd=font(FM,32); for_d=wrap(dr,d,fd,860)[:2]; yy+=14
    for l in for_d: dr.text((64,yy),l,font=fd,fill=(201,211,227)); yy+=46
    dr.text((64,560),'tempalnote.com',font=font(F,30),fill=(227,194,122))
    dr.text((1136,566),'비공식 팬 사이트',font=font(FM,22),fill=(160,170,190),anchor='ra')
    bg.save(f'/home/claude/site/img/og/{k}.jpg',quality=84,optimize=True,progressive=True)
print(len(PAGES),'pages; made',len([k for k in PAGES if k in IMG]))
