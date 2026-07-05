export type AIConfidenceResult = {
  symbol: string;
  ai_confidence: number;
  signal: string;
  risk: string;
  indicators: Record<string, number>;
  summary: string;
};

export type AIConfidenceResponse = Record<string, AIConfidenceResult>;