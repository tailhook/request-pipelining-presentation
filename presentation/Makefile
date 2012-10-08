presentation: diagrams

diagrams: img/pipe.svg

img/pipe_vs_norm.svg: pipe_vs_norm.dot
	mscgen -Tsvg -o $@ $^

img/pipe.svg: pipe.dot
	mscgen -Tsvg -o $@ $^
