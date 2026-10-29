import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p).resolve() != Path(__file__).resolve().parent]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyBboxPatch,Circle
from matplotlib.font_manager import FontProperties
P=Path(__file__).resolve().parent
font=FontProperties(fname='/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
plt.rcParams['font.family']=font.get_name()
plt.rcParams['axes.unicode_minus']=False
BG='#f4f6fa'; INK='#152b42'; GRAY='#8995a5'; BLUE='#3979c6'; GREEN='#128477'
fig=plt.figure(figsize=(15,10),facecolor=BG)
fig.text(.055,.945,'电池仓扩容 · 打印版与新方案',fontsize=25,color=INK,weight='bold')
fig.text(.055,.908,'后盖内侧俯视，同一比例  |  单位 mm  |  外壳外形均为 85 × 45',fontsize=12,color=GRAY)

def dim(ax,a,b,text,color=INK,vertical=False):
 ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='<->',lw=1,color=color,shrinkA=0,shrinkB=0))
 x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
 ax.text(x-1.5 if vertical else x,y if vertical else y+1.2,text,fontsize=10,color=color,ha='right' if vertical else 'center',va='center' if vertical else 'bottom',rotation=90 if vertical else 0,bbox=dict(facecolor=BG,edgecolor='none',pad=1))

def panel(rect,new=False):
 ax=fig.add_axes(rect);ax.set_aspect('equal');ax.set_xlim(-49,47);ax.set_ylim(-30,30);ax.axis('off')
 color=GREEN if new else BLUE
 ax.add_patch(FancyBboxPatch((-42.5,-22.5),85,45,boxstyle='round,pad=0,rounding_size=5.5',fc='#e2e6ed',ec='#748293',lw=1.4))
 ax.add_patch(FancyBboxPatch((-40.5,-20.5),81,41,boxstyle='round,pad=0,rounding_size=3.5',fc='white',ec='#c4ccd6',lw=1))
 for x in [-37.46,37.46]:
  for y in [-17.46,17.46]:
   ax.add_patch(Circle((x,y),3.4,fc='#cbd3dd',ec='#a4aebb'))
   ax.add_patch(Circle((x,y),1.2,fc='white',ec='#a4aebb'))
 ix,iy,iw,ih=(-34,-20.3,57,32) if new else (-30,-18.9,52,30)
 ax.add_patch(Rectangle((ix-1.2,iy-1.2),iw+2.4,ih+2.4,fc=color,ec=color,alpha=.55))
 ax.add_patch(Rectangle((ix,iy),iw,ih,fc='white',ec=color,lw=1.3))
 px,py,pw,ph=(-33.5,-19.8,56,31) if new else (-29.5,-18.4,51,29)
 ax.add_patch(Rectangle((px,py),pw,ph,fc=color,ec=color,alpha=.18))
 ax.add_patch(Rectangle((px,py),pw,ph,fill=False,ec=color,ls='--',lw=1.3))
 ax.text(px+pw/2,py+ph/2+2,'建议电池成品上限',ha='center',color=INK,fontsize=10)
 ax.text(px+pw/2,py+ph/2-3,f'{pw} × {ph} × 3.3',ha='center',color=color,fontsize=16,weight='bold')
 ax.add_patch(FancyBboxPatch((23.8,-12.7),13.2,20.1,boxstyle='round,pad=0,rounding_size=1.8',fc='#e9edf1',ec=GRAY,lw=1.2))
 ax.add_patch(FancyBboxPatch((25.4,-9),10,15,boxstyle='round,pad=0,rounding_size=5',fc='#c4cdd6',ec=GRAY,lw=1))
 ax.text(30.4,-2,'喇\n叭',ha='center',va='center',fontsize=9,color=INK)
 for x,y,w,h in [(-12.439,11.633,4.5,7.6),(-7.939,12.433,3,6),(31.628,7.952,7.6,4.5),(32.428,12.452,6,3)]:
  ax.add_patch(Rectangle((x,y),w,h,fc='#ead7bf',ec='#ac895b',lw=.8))
 ax.text(-10,22.5,'喇叭插座',fontsize=9,ha='center',color='#84633c')
 ax.text(34.5,22.5,'电池插座',fontsize=9,ha='center',color='#84633c')
 dim(ax,(ix,-26),(ix+iw,-26),f'框内长 {iw}',color)
 dim(ax,(-45,iy),(-45,iy+ih),f'框内宽 {ih}',color,True)
 return ax
fig.text(.07,.855,'A  当前打印版 · v0.10',fontsize=17,color=BLUE,weight='bold')
fig.text(.545,.855,'B  扩容方案 · 需新版后盖',fontsize=17,color=GREEN,weight='bold')
panel([.035,.49,.46,.35]);panel([.51,.49,.46,.35],True)
fig.text(.075,.466,'框内 52 × 30   /   成品建议 ≤ 51 × 29 × 3.3',fontsize=12,color=BLUE)
fig.text(.55,.466,'框内 57 × 32   /   成品建议 ≤ 56 × 31 × 3.3',fontsize=12,color=GREEN)
ax=fig.add_axes([.065,.13,.42,.27]);ax.set_aspect('equal');ax.axis('off');ax.set_xlim(-7,65);ax.set_ylim(-8,37)
ax.add_patch(Rectangle((0,0),56,31,fc=GREEN,alpha=.17,ec=GREEN,lw=2))
ax.add_patch(Rectangle((0,0),51,29,fc=BLUE,alpha=.17,ec=BLUE,lw=2))
ax.plot([51,51],[0,29],color=BLUE,lw=1.7);ax.plot([0,51],[29,29],color=BLUE,lw=1.7)
ax.text(22,12,'原成品包络\n51 × 29',color=BLUE,fontsize=14,ha='center')
dim(ax,(51,-4),(56,-4),'+5 mm',GREEN)
ax.annotate('宽度 +2 mm',xy=(38,30),xytext=(38,36),ha='center',color=GREEN,fontsize=10,arrowprops=dict(arrowstyle='->',color=GREEN))
fig.text(.065,.411,'成品电池包络叠加对比',fontsize=14,color=INK,weight='bold')
fig.text(.55,.366,'+17.4%',fontsize=34,color=GREEN,weight='bold')
fig.text(.55,.324,'可用电池平面面积增加，厚度上限保持 3.3 mm',fontsize=12,color=INK)
fig.text(.55,.268,'扩容后模型关键间隙',fontsize=13,color=INK,weight='bold')
fig.text(.55,.232,'Type-C 下方 0.40  ·  喇叭插座 0.43  ·  ESP32 下方 0.68',fontsize=11,color=INK)
fig.text(.55,.184,'建议购买标称 3 mm 厚电池，成品尺寸包含保护板与包边。',fontsize=11,color=INK)
fig.text(.55,.149,'扩容方案已通过静态相交检查，仍需实物装配验证。',fontsize=11,color=INK)
fig.text(.055,.065,'说明：结构为尺寸示意，省略卡槽、导轨及部分元件；上方连接器为 PCB 上的投影位置。',fontsize=10,color=GRAY)
fig.text(.055,.039,'下方叠加图按同一角对齐以比较尺寸，不代表实际安装位置；本次仅生成对比图。',fontsize=10,color=GRAY)
fig.savefig(P/'电池扩容前后对比.png',dpi=160,facecolor=BG)
fig.savefig(P/'电池扩容前后对比.pdf',facecolor=BG)
