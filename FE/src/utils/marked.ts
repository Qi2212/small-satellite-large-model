import "highlight.js/scss/idea.scss";
import { Marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";

export const marked = new Marked(
  markedHighlight({
    langPrefix: "hljs language-",
    highlight(code: any, lang: string) {
      const language = hljs.getLanguage(lang) ? lang : "plaintext";
      return hljs.highlight(code, { language }).value;
    },
  })
);
