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
    source: string;
    chunk_index: number;
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

    const question = input.trim();

    // Push user message to chat UI
    const userMessage: Message = { role: "user", content: question };
    setMessages(prev => [...prev, userMessage]);

    setInput("");
    setIsLoading(true);

    try {
      // Choose workspace_id (same as upload)
      const workspaceId = assistantName.replace(/\s+/g, "_").toLowerCase();

      const response = await fetch(`https://autoragos.onrender.com/api/workspaces/${workspaceId}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Request failed");
      }

      const data = await response.json();
      const rag = data.rag_result;

      // Create assistant message from API result
      const assistantMessage: Message = {
        role: "assistant",
        content: rag.answer,
        confidence: rag.confidence,
        citations: rag.citations,
        needsReview: rag.needs_human_review
      }

      // Add assistant message to UI
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        role: "assistant",
        content: `⚠️ Error: ${err.message || "Something went wrong"}`,
        confidence: 0,
        citations: [],
        needsReview: true,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
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

                  {message.role === "assistant" && message.confidence > 0 && (
                    <div className="mt-4 pt-4 border-t border-border space-y-3">
                      {/* Confidence */}
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-muted-foreground">Confidence:</span>
                        <span className={`font-semibold ${message.confidence >= 0.8 ? "text-success" : message.confidence >= 0.7 ? "text-warning" : "text-destructive"}`}>
                          {(message.confidence * 100).toFixed(0)}%
                        </span>
                      </div>

                      {/* Citations */}
                      {message.citations && (() => {
                        const uniqueCitations = [];
                        const seen = new Set();

                        message.citations.forEach(c => {
                          if (!seen.has(c.source)) {
                            seen.add(c.source);
                            uniqueCitations.push(c);
                          }
                        });

                        return (
                          <div className="space-y-2">
                            <p className="text-sm text-muted-foreground">Sources:</p>

                            {uniqueCitations.map((citation, i) => (
                              <div key={i} className="bg-muted/50 rounded p-2 text-sm">
                                <div className="flex items-center gap-2 mb-1">
                                  <FileText className="h-3 w-3" />
                                  <span className="font-medium">{citation.source}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        );
                      })()}

                      {/* Review Warning */}
                     
                    </div>
                  )}
                   {message.role === "assistant"  && message.confidence == 0 && message.needsReview && (
                        <div className="flex items-center gap-2 text-sm text-warning">
                          <AlertTriangle className="h-4 w-4" />
                          <span>Needs human review</span>
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
