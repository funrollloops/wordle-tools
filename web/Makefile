all: words.js match.js

words.ts: ../words.txt Makefile
	(echo 'export const WORDS="'; cat "$<"; echo '";') | tr -d '\n' > $@

%.js: %.ts node_modules
	tsc $<

node_modules: package.json package-lock.json
	npm install
	touch node_modules
