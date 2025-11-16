import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sparkles, Send, BarChart3, AlertTriangle, FileText } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Message {
  role: "user" | "assistant";
  content: string;
  confidence?: number;
  citations?: Array<{
    doc: string;
    section: string;
    snippet: string;
  }>;
  needsReview?: boolean;
}

const Chat = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { assistantName = "Your Assistant", qualityScore = 81 } = location.state || {};

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Hi! I'm ${assistantName}. I've analyzed your documents and I'm ready to help. Ask me anything!`,
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const exampleQuestions = [
    "What are the key points in the uploaded documents?",
    "Summarize the main topics covered",
    "What policies are mentioned?"
  ];

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const confidence = Math.random() * 0.3 + 0.7; // 0.7 to 1.0
      const needsReview = confidence < 0.75;

      const assistantMessage: Message = {
        role: "assistant",
        content: "Based on the documents you've uploaded, here's what I found: The policy clearly states that employees must follow the guidelines outlined in section 3.2. This includes adhering to safety protocols and maintaining proper documentation.",
        confidence: parseFloat(confidence.toFixed(2)),
        citations: [
          {
            doc: "HR_Policy_2024.pdf",
            section: "Section 3.2: Employee Guidelines",
            snippet: "...employees must follow the guidelines outlined..."
          }
        ],
        needsReview
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleExampleQuestion = (question: string) => {
    setInput(question);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-primary" />
            <div>
              <h1 className="font-bold text-lg">{assistantName}</h1>
              <p className="text-sm text-muted-foreground">Quality Score: {qualityScore}%</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/dashboard", { state: { assistantName, qualityScore } })}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Dashboard
          </Button>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="container mx-auto max-w-4xl space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`max-w-[80%] ${message.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border border-border"} rounded-lg p-4`}>
                  <p className="mb-2">{message.content}</p>
                  
                  {message.role === "assistant" && message.confidence && (
                    <div className="mt-4 pt-4 border-t border-border space-y-3">
                      {/* Confidence */}
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-muted-foreground">Confidence:</span>
                        <span className={`font-semibold ${message.confidence >= 0.8 ? "text-success" : message.confidence >= 0.7 ? "text-warning" : "text-destructive"}`}>
                          {(message.confidence * 100).toFixed(0)}%
                        </span>
                      </div>

                      {/* Citations */}
                      {message.citations && (
                        <div className="space-y-2">
                          <p className="text-sm text-muted-foreground">Sources:</p>
                          {message.citations.map((citation, i) => (
                            <div key={i} className="bg-muted/50 rounded p-2 text-sm">
                              <div className="flex items-center gap-2 mb-1">
                                <FileText className="h-3 w-3" />
                                <span className="font-medium">{citation.doc}</span>
                              </div>
                              <p className="text-xs text-muted-foreground">{citation.section}</p>
                              <p className="text-xs italic mt-1">{citation.snippet}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Review Warning */}
                      {message.needsReview && (
                        <div className="flex items-center gap-2 text-sm text-warning">
                          <AlertTriangle className="h-4 w-4" />
                          <span>Needs human review</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-card border border-border rounded-lg p-4">
                  <div className="flex gap-2">
                    <div className="h-2 w-2 bg-primary rounded-full animate-bounce" />
                    <div className="h-2 w-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                    <div className="h-2 w-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Example Questions */}
        {messages.length === 1 && (
          <div className="px-4 py-3 border-t border-border bg-muted/30">
            <div className="container mx-auto max-w-4xl">
              <p className="text-sm text-muted-foreground mb-2">Try asking:</p>
              <div className="flex flex-wrap gap-2">
                {exampleQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleExampleQuestion(question)}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Input */}
        <div className="border-t border-border bg-card p-4">
          <div className="container mx-auto max-w-4xl flex gap-2">
            <Input
              placeholder="Ask your assistant..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              className="flex-1"
            />
            <Button onClick={handleSend} disabled={!input.trim() || isLoading}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
