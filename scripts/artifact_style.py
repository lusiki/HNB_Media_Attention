"""Shared publication palette and bundled, licensed typography."""
from pathlib import Path

SITE=Path(__file__).resolve().parents[1]
FONT_DIR=SITE/'assets/fonts'
PAPER='#F7F4EC'
INK='#172A32'
BLUE='#2454CF'
MUTED='#53636A'
RULE='#D5D7CF'
PALE='#E9EDF6'
COPPER='#A95836'
FONTS={'Sans':'SourceSans3-Regular.ttf','Sans-Bold':'SourceSans3-Semibold.ttf',
       'Serif':'SourceSerif4-Regular.ttf','Serif-Italic':'SourceSerif4-It.ttf',
       'Display':'SourceSerif4Display-Regular.ttf'}

def register_pdf_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for label,name in FONTS.items():pdfmetrics.registerFont(TTFont(label,str(FONT_DIR/name)))
    pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Sans-Bold',italic='Sans',boldItalic='Sans-Bold')
    pdfmetrics.registerFontFamily('Serif',normal='Serif',italic='Serif-Italic',bold='Serif',boldItalic='Serif-Italic')

def configure_matplotlib():
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for name in FONTS.values():font_manager.fontManager.addfont(str(FONT_DIR/name))
    plt.rcParams.update({'font.family':'Source Sans 3','font.size':15,
        'text.color':INK,'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,
        'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,
        'axes.facecolor':PAPER,'figure.facecolor':PAPER,'savefig.facecolor':PAPER,
        'svg.fonttype':'path','pdf.fonttype':42,'axes.unicode_minus':False})
