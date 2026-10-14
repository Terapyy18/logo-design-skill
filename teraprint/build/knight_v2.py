from lib import svg
K = ("M 140 20 "
     "C 132 32 128 42 127 52 "          # ear front
     "C 122 56 118 60 114 64 "          # brow
     "C 96 82 70 104 52 124 "           # nose line
     "C 40 136 36 150 46 160 "          # muzzle front
     "C 54 168 66 166 76 158 "          # lip
     "C 88 154 100 152 110 152 "        # jaw underside
     "C 122 154 124 166 116 176 "       # jaw corner / throat
     "C 98 196 84 208 82 226 "          # chest
     "L 206 226 "
     "C 214 186 212 128 190 86 "        # back / mane
     "C 180 66 166 52 152 46 "          # back of head
     "C 148 38 144 28 140 20 Z "        # ear back
     "M 124 90 C 124 95 120 98 116 98 C 112 98 108 95 108 90 C 108 86 112 83 116 83 C 120 83 124 86 124 90 Z")
open("../concepts/knight-base-v2.svg","w").write(svg([K]))
