from pathlib import Path
from html import escape
from math import hypot
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT=Path(__file__).parent
# Hand-drawn coordinates use a 100×100 drafting square.
# Japanese and Chinese use connected brush strokes; English uses one silhouette per glyph.
J={
'ス':[[(11,11),(91,9),(67,49),(21,89)],[(52,53),(89,88)]],
'タ':[[(20,43),(34,10),(42,21),(86,25),(63,69),(23,90)],[(29,49),(63,63)]],
'ー':[[(9,53),(91,47)]],
'ト':[[(35,11),(38,88)],[(40,44),(88,66)]],
'リ':[[(27,16),(29,61)],[(77,14),(73,61),(45,87)]],
'ン':[[(18,23),(41,42)],[(20,82),(75,58),(88,20)]],
'グ':[[(43,4),(18,52)],[(38,23),(77,25),(59,65),(29,87)],[(78,3),(84,17)],[(91,4),(97,18)]],
'よ':[[(54,13),(56,77)],[(55,43),(88,43)],[(54,71),(39,82),(21,73)],[(21,73),(29,62),(48,62)],[(48,62),(77,82)]],
'り':[[(28,16),(30,57)],[(76,13),(74,61),(46,87)]],
}
ENGLISH={
 'A':{'outer':[(2,91),(2,83),(10,83),(37,11),(62,11),(91,83),(99,83),(99,91),(72,91),(64,65),(36,65),(28,91)],'holes':[[(42,49),(58,49),(51,28)]],'facet':[(42,49),(58,49),(64,65),(36,65)]},
 'E':{'outer':[(12,12),(85,11),(88,13),(87,31),(31,31),(31,45),(76,44),(77,58),(31,59),(31,70),(88,70),(89,81),(97,81),(97,88),(12,88)],'facets':[[(12,12),(85,11),(88,13),(87,31),(31,31)]]},
 'F':{'outer':[(12,12),(84,11),(87,13),(87,29),(31,29),(31,45),(73,44),(75,59),(74,61),(31,61),(31,79),(39,79),(39,88),(5,88),(5,79),(12,79),(12,20),(4,20),(4,12)],'facets':[[(12,12),(84,11),(87,13),(87,29),(31,29)]]},
 'G':{'outer':[(82,12),(82,29),(36,29),(29,36),(29,64),(36,72),(68,72),(68,62),(55,62),(55,49),(86,49),(86,76),(73,88),(25,88),(11,74),(11,26),(25,12)],'facet':[(55,49),(86,49),(68,62),(55,62)]},
 'H':{'outer':[(11,12),(32,11),(32,43),(71,42),(71,12),(87,12),(87,88),(71,88),(71,58),(32,59),(32,88),(5,88),(5,81),(11,81)],'facets':[[(32,43),(71,42),(71,58),(32,59)]]},
 'I':{'outer':[(10,12),(76,11),(78,27),(57,27),(57,73),(82,74),(82,88),(24,88),(23,73),(39,73),(39,28),(10,29)]},
 'M':{'outer':[(1,88),(1,81),(10,81),(10,11),(31,11),(49,44),(70,11),(88,11),(88,88),(65,88),(65,81),(73,81),(73,41),(51,69),(47,69),(31,41),(31,88)],'facets':[[(70,11),(88,11),(73,41)],[(1,88),(1,81),(10,81),(10,11),(31,11),(31,41),(31,88)]]},
 'N':{'outer':[(3,90),(3,83),(12,83),(12,12),(34,12),(68,55),(68,12),(96,12),(96,20),(85,20),(85,88),(67,88),(32,44),(32,83),(39,83),(39,90)],'facets':[[(68,12),(96,12),(96,20),(85,20)]]},
 'O':{'outer':[(19,11),(81,11),(89,19),(89,81),(81,89),(19,89),(11,81),(11,19)],'holes':[[(34,32),(71,32),(74,35),(74,69),(71,72),(34,72),(31,69),(31,35)]],'facets':[[(81,11),(89,19),(89,81),(74,69),(74,35),(71,32)]]},
 'R':{'outer':[(13,12),(62,12),(86,38),(62,63),(59,63),(89,83),(95,83),(95,89),(68,89),(43,66),(31,66),(31,89),(13,89)],'holes':[[(31,31),(57,31),(68,38),(57,49),(31,49)]],'facets':[[(62,12),(86,38),(62,63),(59,63),(57,49),(68,38),(57,31)],[(59,63),(62,63),(89,83),(95,83),(95,89),(68,89),(43,66)]]},
 'S':{'outer':[(96,11),(96,42),(82,42),(82,31),(29,31),(29,51),(72,51),(86,55),(86,77),(75,88),(0,89),(0,63),(18,63),(18,72),(69,72),(69,65),(28,65),(12,60),(12,26),(23,12)],'facets':[[(96,11),(96,42),(82,42),(82,31),(29,31),(23,12)],[(0,89),(0,63),(18,63),(18,72)]]},
 'T':{'outer':[(11,12),(60,11),(91,10),(91,28),(60,28),(59,81),(71,81),(71,89),(35,89),(35,82),(42,82),(43,30),(10,30)],'facet':[(60,11),(91,10),(91,28),(60,28)]},
}
# Finished glyph contours. Each outer silhouette is drafted as one continuous
# polygon; remaining contours are counters or separate radical shapes.
ZH_CONTOURS={
 '来':[
  [(44,94),(43,70),(18,90),(10,84),(35,59),(9,61),(7,49),(43,45),(43,25),(13,28),(10,16),(42,12),(42,9),(55,7),(56,12),(88,12),(91,22),(56,24),(56,44),(90,46),(92,58),(65,58),(91,83),(87,90),(57,69),(58,91)],
  [(69,45),(63,41),(73,27),(81,31)],
  [(35,46),(25,34),(30,28),(40,40)],
 ],
 '自':[
  [(13,92),(15,21),(25,17),(29,7),(39,9),(36,15),(80,13),(88,17),(89,90),(85,95),(53,98)],
  [(27,28),(52,25),(74,25),(74,39),(28,40)],
  [(26,49),(75,48),(75,59),(26,60)],
  [(26,70),(75,69),(75,83),(27,83)],
 ],
 '星':[
  [(14,99),(13,88),(44,84),(29,83),(27,74),(45,73),(44,69),(30,69),(29,61),(44,60),(44,52),(17,51),(17,10),(50,2),(82,8),(84,51),(58,53),(58,60),(77,59),(79,69),(58,69),(58,74),(79,73),(81,83),(58,84),(58,85),(88,87),(89,99)],
  [(29,17),(50,14),(71,16),(71,26),(29,26)],
  [(28,34),(71,34),(71,43),(29,44)],
 ],
 '的':[
  [(12,92),(11,27),(25,22),(29,9),(38,9),(35,21),(58,20),(61,25),(60,93)],
  [(23,32),(50,31),(50,46),(23,47)],
  [(23,56),(51,55),(51,82),(23,82)],
  [(70,14),(79,16),(76,24),(94,22),(98,27),(96,79),(83,94),(75,90),(83,76),(85,34),(63,38)],
  [(64,50),(79,59),(74,67),(61,57)],
 ],
 '弦':[
  [(46,92),(35,93),(28,88),(30,82),(38,85),(41,73),(9,73),(8,43),(12,38),(40,37),(41,24),(14,24),(10,14),(29,10),(47,11),(52,18),(49,41),(46,47),(20,48),(20,62),(47,62),(53,68)],
  [(64,86),(59,77),(70,62),(58,62),(52,54),(69,35),(55,36),(53,25),(98,23),(101,35),(80,35),(71,51),(82,52),(89,59),(76,73),(94,72),(95,82)],
 ],
 '乐':[
  [(51,96),(45,90),(51,81),(51,56),(24,58),(17,53),(24,22),(29,17),(68,6),(72,14),(34,27),(31,44),(51,43),(51,32),(65,30),(65,43),(88,44),(90,56),(65,56),(65,89)],
  [(88,88),(74,73),(80,65),(94,82)],
  [(20,88),(14,84),(26,67),(34,71)],
 ],
}
ZH_OVERLAYS={
 # Colored apostrophe-like polygons deliberately cross the main strokes.
 '星':[
  ([(30,47),(38,50),(27,70),(19,65)],'#9588cf'),
 ],
 '弦':[
  ([(73,8),(80,6),(89,27),(81,31)],'#9689d0'),
  ([(88,78),(97,76),(107,95),(100,102)],'#9588cf'),
 ],
}
ZH_CUTS={
 # Approximate endpoints snap to actual corners of the finished silhouette.
 '来':[((49,9),(51,93),(100,50),'#7787c9'),
       ((51,55),(89,88),(100,100),'#9182c8')],
 '自':[((52,19),(81,89),(100,48),'#7c86ca')],
 '星':[((50,9),(51,94),(100,50),'#7a87ca'),
       ((51,54),(88,93),(100,100),'#9182c8')],
 '的':[((57,24),(79,91),(100,48),'#7b87ca'),
       ((88,51),(79,91),(100,100),'#9181c9')],
 '弦':[((48,17),(64,80),(100,48),'#7787c9'),
       ((82,56),(100,94),(101,101),'#9182c9')],
 '乐':[((58,31),(58,93),(100,48),'#7887ca'),
       ((58,50),(91,85),(100,100),'#9082c9')],
}
TITLES={
 'ja':(['スタースト','リングスより'],'スターストリングスより',J,166,15),
 'en':(['STRINGS','FROM THE','STARS'],'STRINGS FROM THE STARS',ENGLISH,135,0),
}
COLORS=['#4d68b8','#6659b2','#3d58a5']
EN_X_RHYTHM=[.88,.82,.87,.83,.91,.85]
EN_Y_RHYTHM=[1.36,1.42,1.40,1.33,1.45,1.39]
EN_SIZE={'S':(.92,1.14),'R':(1.10,1.08),'M':(1.30,.91),'O':(.92,.92)}
EN_RELATIVE_SMALL={(0,i):.94 for i in range(1,6)} | {(2,i):.94 for i in range(1,4)}
EN_ROW_START=(0,7,14)
EN_JITTER=[[-4,7,-10,5,-8,8,0],[10,-6,14,-4,0,8,-5,11],[-8,9,-7,7,-2]]
EN_ANGLE=[[-2.5,2.0,-2.5,1.6,-2.0,2.5,-1.0],[2.0,-2.5,1.7,-1.7,0,2.3,-1.3,2.0],[-2.3,2.0,-1.6,2.2,-1.8]]
def english_width_rhythm(ch,idx,rowno):
 base=1.27 if ch=='O' else EN_X_RHYTHM[idx%6]*(.89 if rowno==1 else 1)
 factor=1.19 if rowno==1 and idx>=11 else 1
 flatten=1 if ch in 'SR' else 1.035
 return base*EN_SIZE.get(ch,(1.04,1.12))[0]*factor*EN_RELATIVE_SMALL.get((rowno,idx-EN_ROW_START[rowno]),1)*flatten
def english_height_rhythm(ch,idx,rowno):
 base=1.30 if ch=='O' else EN_Y_RHYTHM[idx%6]
 factor=.82 if rowno==1 and idx>=11 else 1
 flatten=1 if ch in 'SR' else .97
 return base*EN_SIZE.get(ch,(1.04,1.12))[1]*factor*EN_RELATIVE_SMALL.get((rowno,idx-EN_ROW_START[rowno]),1)*flatten
BRANCHES={
 'ja':{'ス':1,'タ':1,'ト':1,'ン':0,'グ':0,'よ':1,'り':0},
}
STROKE_WIDTHS={
 'ja':{
  'ス':{0:[23,22,15,10],1:[11,9]},
  'タ':{0:[12,15,18,17,13,9],1:[8,7]},
  'グ':{0:[22,9],2:[3,2.5],3:[3,2.5]},
 },

}

def ribbon(points, base, taper=False, widths_override=None, end_cut_ratio=.12):
 """Single polygon from a continuous line. Main stems have uniform width."""
 normals=[]; directions=[]
 for (x1,y1),(x2,y2) in zip(points,points[1:]):
  length=hypot(x2-x1,y2-y1) or 1
  ux,uy=(x2-x1)/length,(y2-y1)/length
  directions.append((ux,uy)); normals.append((-uy,ux))
 widths=list(widths_override) if widths_override else [base for _ in points]
 if taper and not widths_override:
  widths[-1]=base*.78
 left=[];right=[]
 for i,(x,y) in enumerate(points):
  if i==0: nx,ny=normals[0];ux,uy=directions[0];miter=1
  elif i==len(points)-1: nx,ny=normals[-1];ux,uy=directions[-1];miter=1
  else:
   ax,ay=normals[i-1][0]+normals[i][0],normals[i-1][1]+normals[i][1]
   mag=hypot(ax,ay) or 1
   nx,ny=ax/mag,ay/mag
   dot=abs(nx*normals[i][0]+ny*normals[i][1]) or 1
   miter=min(1.55,1/dot)
   ux,uy=0,0
  half=widths[i]*miter/2
  # Offset the cut ends asymmetrically. This makes the terminals oblique.
  cut=widths[i]*end_cut_ratio if i in (0,len(points)-1) else 0
  left.append((x+nx*half+ux*cut,y+ny*half+uy*cut))
  right.append((x-nx*half-ux*cut,y-ny*half-uy*cut))
 outline=left+right[::-1]
 return 'M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in outline)+' Z'

def letter_svg(ch,strokes,idx,x,y,scale,angle,width,kind):
 # The filter outlines the UNION of these touching polygons, not each stroke.
 trans=f'translate({x:.1f} {y:.1f}) rotate({angle}) scale({scale:.3f})'
 color=[]
 for k,pts in enumerate(strokes):
  branch=BRANCHES[kind].get(ch)==k
  override=STROKE_WIDTHS.get(kind,{}).get(ch,{}).get(k)
  path=ribbon(pts,width,branch,override,0 if kind=='en' else .12)
  if kind=='en': primary=('#4d68b8' if idx<7 else '#6c5eb7' if idx<11 else '#405ba7' if idx<14 else '#685bb4')
  elif kind=='zh': primary=('#4d68b8' if idx<4 else '#6659b2')
  else: primary=COLORS[idx%len(COLORS)]
  hue='#9082cf' if branch else primary
  color.append(f'<path id="stroke-{idx+1}-{k+1}" d="{path}" fill="{hue}"/>')
 return f'<g id="letter-{idx+1}" data-letter="{escape(ch)}" transform="{trans}"><g filter="url(#unified-outline)">{"".join(color)}</g></g>'

def polygon_path(points):
 return 'M '+' L '.join(f'{x},{y}' for x,y in points)+' Z'

def chinese_silhouette(ch):
 return ZH_CONTOURS[ch]

def halfplane_polygon(a,b,inside):
 # A color boundary is a line through two vertices of the finished silhouette.
 x1,y1=a;x2,y2=b
 side=(x2-x1)*(inside[1]-y1)-(y2-y1)*(inside[0]-x1)
 sign=1 if side>=0 else -1
 def distance(p):return sign*((x2-x1)*(p[1]-y1)-(y2-y1)*(p[0]-x1))
 box=[(-20,-20),(120,-20),(120,120),(-20,120)];out=[]
 for p,q in zip(box,box[1:]+box[:1]):
  dp,dq=distance(p),distance(q)
  if dp>=0:out.append(p)
  if (dp<0 and dq>0) or (dp>0 and dq<0):
   t=dp/(dp-dq);out.append((round(p[0]+(q[0]-p[0])*t,1),round(p[1]+(q[1]-p[1])*t,1)))
 return out

def chinese_letter_svg(ch,idx):
 rings=chinese_silhouette(ch)
 silhouette=' '.join(polygon_path(ring) for ring in rings)
 vertices=[p for ring in rings for p in ring]
 clip=f'clip-zh-{idx+1}'
 facets=[]
 for j,(target_a,target_b,inside,color) in enumerate(ZH_CUTS[ch]):
  a=min(vertices,key=lambda p:hypot(p[0]-target_a[0],p[1]-target_a[1]))
  b=min(vertices,key=lambda p:hypot(p[0]-target_b[0],p[1]-target_b[1]))
  cut=halfplane_polygon(a,b,inside)
  facets.append(f'<path id="zh-facet-{idx+1}-{j+1}" data-cut-vertices="{a[0]},{a[1]} {b[0]},{b[1]}" d="{polygon_path(cut)}" fill="{color}" clip-path="url(#{clip})"/>')
 overlays=''.join(f'<path id="zh-overlay-{idx+1}-{j+1}" d="{polygon_path(points)}" fill="{color}"/>'
                  for j,(points,color) in enumerate(ZH_OVERLAYS.get(ch,[])))
 return (f'<g id="zh-letter-{idx+1}" data-letter="{ch}">'
         f'<defs><clipPath id="{clip}" clipPathUnits="userSpaceOnUse"><path d="{silhouette}" clip-rule="evenodd"/></clipPath></defs>'
         f'<g filter="url(#unified-outline)"><path id="zh-silhouette-{idx+1}" d="{silhouette}" fill="#4d63ad" fill-rule="evenodd"/>{"".join(facets)}{overlays}</g></g>')

def build_chinese_title():
 rows=['来自星星','的弦乐'];title=''.join(rows);rendered=[];idx=0
 widths=[[1.01,.96,1.06,1.03],[1.08,1.07,1.03]]
 heights=[[1.04,1.00,1.08,1.02],[1.06,1.07,1.03]]
 angles=[[-2.2,1.5,-1.6,1.7],[1.2,-1.8,1.3]]
 y_offsets=[[-2,5,-6,3],[0,-5,3]]
 for rowno,row in enumerate(rows):
  step=[160,190][rowno];scale=[1.48,1.56][rowno]
  start=(800-((len(row)-1)*step+scale*110))/2
  for col,ch in enumerate(row):
   x=start+col*step;y=[18,218][rowno]+y_offsets[rowno][col]
   sx=scale*widths[rowno][col];sy=scale*heights[rowno][col]
   rendered.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({angles[rowno][col]}) scale({sx:.3f} {sy:.3f})">{chinese_letter_svg(ch,idx)}</g>')
   idx+=1
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400" role="img" aria-label="{title}">
<title>{title}</title><desc>Two-line, hand-drawn Chinese title: 来自星星 above 的弦乐. Editable angular polygon silhouettes.</desc>
<defs><filter id="unified-outline" x="-25%" y="-25%" width="165%" height="170%" color-interpolation-filters="sRGB"><feMorphology in="SourceAlpha" operator="dilate" radius="3.2" result="shape"/><feGaussianBlur in="shape" stdDeviation="2.3" result="blur"/><feOffset in="blur" dx="5" dy="7" result="offset"/><feFlood flood-color="#1b245e" flood-opacity=".43" result="shadow-color"/><feComposite in="shadow-color" in2="offset" operator="in" result="shadow"/><feFlood flood-color="#fff" result="white"/><feComposite in="white" in2="shape" operator="in" result="outline"/><feMerge><feMergeNode in="shadow"/><feMergeNode in="outline"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<g id="hand-drawn-title">{''.join(rendered)}</g></svg>'''
 path=OUT/'star-strings-zh.svg';path.write_text(svg)
 print(path.name,len(title),'directly drawn Chinese silhouettes',sum(len(ZH_CONTOURS[c]) for c in title),'contours')

def english_letter_svg(ch,shape,idx):
 """One compound silhouette, then a clipped facet at a projecting stroke."""
 outline=polygon_path(shape['outer'])+''.join(' '+polygon_path(h) for h in shape.get('holes',[]))
 primary='#4d68b8' if idx<7 else '#6c5eb7' if idx<14 else '#485da9'
 clip=f'clip-letter-{idx+1}'
 facet=''
 for j,points in enumerate(shape.get('facets',[]) + ([shape['facet']] if 'facet' in shape else [])):
  hue='#9184d2' if j%2==0 else '#6e78c6'
  facet+=f'<path id="facet-{idx+1}-{j+1}" d="{polygon_path(points)}" fill="{hue}" clip-path="url(#{clip})"/>'
 return (f'<g id="letter-{idx+1}" data-letter="{ch}">'
         f'<defs><clipPath id="{clip}" clipPathUnits="userSpaceOnUse"><path d="{outline}" clip-rule="evenodd"/></clipPath></defs>'
         f'<g filter="url(#unified-outline)"><path id="silhouette-{idx+1}" d="{outline}" fill="{primary}" fill-rule="evenodd"/>{facet}</g></g>')

def light_english(lines,center,baselines,font_size,colors,outline_width=0,prefix='english',width_factor=1.18,height_factor=.73):
 """Convert a light, broad Avenir Next title to editable vector paths."""
 font=TTFont('/System/Library/Fonts/Avenir Next.ttc',fontNumber=10)
 glyphset=font.getGlyphSet(); cmap=font.getBestCmap(); units=font['head'].unitsPerEm
 sx=font_size/units*width_factor; sy=font_size/units*height_factor
 result=[]
 for row,line in enumerate(lines):
  advances=[font['hmtx'][cmap[ord(ch)]][0]*sx if ch!=' ' else font_size*.36 for ch in line]
  spacing=font_size*.075
  x=center-(sum(advances)+spacing*(len(line)-1))/2
  for i,(ch,adv) in enumerate(zip(line,advances)):
   if ch!=' ':
    pen=SVGPathPen(glyphset)
    glyphset[cmap[ord(ch)]].draw(TransformPen(pen,(sx,0,0,-sy,x,baselines[row])))
    stroke=f' stroke="#fff" stroke-width="{outline_width}" stroke-linejoin="round" paint-order="stroke fill"' if outline_width else ''
    result.append(f'<path id="{prefix}-{row+1}-{i+1}" data-letter="{ch}" d="{pen.getCommands()}" fill="{colors[row]}"{stroke}/>')
   x+=adv+spacing
 return ''.join(result)

def build(key):
 if key=='zh':return build_chinese_title()
 rows,title,glyphs,cell,width=TITLES[key]
 rendered=[];idx=0
 for rowno,row in enumerate(rows):
  chars=list(row)
  rowcell=([130,103,160][rowno] if key=='en' else cell)
  step=rowcell*(.81 if key=='ja' else .84)
  space=rowcell*.18 if key=='en' else 0
  if key=='en':
   gap=3.5
   def latin_span(ch,i):
    xs=[px for px,_ in glyphs[ch]['outer']]
    return (max(xs)-min(xs))*rowcell/100*english_width_rhythm(ch,i,rowno)
   letter_count=sum(c!=' ' for c in chars)
   total=sum(latin_span(c,idx+i) for i,c in enumerate(c for c in chars if c!=' '))+gap*(letter_count-1)+space*chars.count(' ')
  else:
   total=sum(step for _ in chars)
  x=(1200-total)/2-(55 if key=='ja' else 0)
  for position,c in enumerate(chars):
   if c==' ':x+=space;continue
   width_rhythm=([.96,1.04,.99,1.02,.96,1.03][idx%6] if key=='ja' else [1.02,.95,1.03,.98,.91,1.06,1.02][idx] if key=='zh' else english_width_rhythm(c,idx,rowno))
   height_rhythm=([1.13,1.08,1.17,1.1,1.14,1.09][idx%6] if key=='ja' else [1.12,1.04,1.09,1.13,1.03,1.12,1.08][idx] if key=='zh' else english_height_rhythm(c,idx,rowno))
   scale=rowcell/100
   jitter=([-9,7,-4,9,-6,3][idx%6] if key=='ja' else [0,8,-3,4,5,-3,2][idx] if key=='zh' else EN_JITTER[rowno][position])
   angle=([-4,3,-2,4,-3,2][idx%6] if key=='ja' else [-3,2,-2,1,2,-3,2][idx] if key=='zh' else EN_ANGLE[rowno][position])
   y=([38,248] if key=='ja' else [25,215] if key=='zh' else [0,180,325])[rowno]+jitter
   inner=english_letter_svg(c,glyphs[c],idx) if key=='en' else letter_svg(c,glyphs[c],idx,0,0,1,0,width,key)
   origin=x
   if key=='en':
    xs=[px for px,_ in glyphs[c]['outer']]
    origin=x-min(xs)*scale*width_rhythm
   rendered.append((c,f'<g transform="translate({origin:.1f} {y:.1f}) rotate({angle}) scale({scale*width_rhythm:.3f} {scale*height_rhythm:.3f})">{inner}</g>'))
   x+=latin_span(c,idx)+gap if key=='en' else step
   idx+=1
 if key=='ja':
  # Keep the katakana coordinates, but paint グ last so it is in front.
  artwork=''.join(s for ch,s in rendered if ch!='グ')+''.join(s for ch,s in rendered if ch=='グ')
  artwork+=f'<g id="english-side-title">{light_english(["STRINGS","FROM THE","STARS"],985,[70,96,122],23,["#171717"]*3,outline_width=1.4,prefix="side",width_factor=1.0,height_factor=.94)}</g>'
  height=465;svg_width=1120;viewbox='70 0 1120 465'
 else:
  artwork=''.join(s for _,s in rendered)
  height=600 if key=='en' else 450
  svg_width=820 if key=='en' else 800
  viewbox=f'{190 if key=="en" else 200} 0 {svg_width} {height}'
 desc=('Each English glyph is one editable silhouette with optional counters. Accent polygons are clipped within the silhouette.' if key=='en' else 'Hand-drawn editable vector stroke paths, with a unified white border and cast shadow.')
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{height}" viewBox="{viewbox}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<desc>{desc}</desc>
<defs><filter id="unified-outline" x="-25%" y="-25%" width="165%" height="170%" color-interpolation-filters="sRGB"><feMorphology in="SourceAlpha" operator="dilate" radius="3.2" result="shape"/><feGaussianBlur in="shape" stdDeviation="2.3" result="blur"/><feOffset in="blur" dx="5" dy="7" result="offset"/><feFlood flood-color="#1b245e" flood-opacity=".43" result="shadow-color"/><feComposite in="shadow-color" in2="offset" operator="in" result="shadow"/><feFlood flood-color="#fff" result="white"/><feComposite in="white" in2="shape" operator="in" result="outline"/><feMerge><feMergeNode in="shadow"/><feMergeNode in="outline"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<g id="hand-drawn-title">{artwork}</g>
</svg>'''
 path=OUT/f'star-strings-{key}.svg';path.write_text(svg)
 path_count=sum(1+len(glyphs[c].get('holes',[])) for row in rows for c in row if c!=' ') if key=='en' else sum(len(glyphs[c]) for row in rows for c in row if c!=' ')
 print(path.name,len(rendered),'letters',path_count,'silhouette contours' if key=='en' else 'hand paths')
for key in ('ja','zh','en'):build(key)
