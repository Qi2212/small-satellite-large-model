export type Mode = "similarText" | "enhancedAnswer" | "rawAnswer";

interface Answer {
  content: string;
  text: string;
  status: string;
}

export interface Chat{
  question: string;
  rawAnswer: Answer;
  enhancedAnswer: Answer;
  similarText: Answer;
  activeAnswer: Mode;
}