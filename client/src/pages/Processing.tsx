import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Sparkles, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ProcessingStep {
  label: string;
  status: "pending" | "processing" | "complete";
}

const Processing = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { assistantName, fileCount } = location.state || { assistantName: "Your Assistant", fileCount: 0 };

  const [steps, setSteps] = useState<ProcessingStep[]>([
    { label: "Extracting text via Gemini (OCR, STT)", status: "pending" },
    { label: "Cleaning and chunking", status: "pending" },
    { label: "Creating embeddings (Qdrant)", status: "pending" },
    { label: "Building chat pipeline", status: "pending" },
    { label: "Generating test questions", status: "pending" },
    { label: "Scoring your assistant", status: "pending" },
  ]);

  const [qualityScore, setQualityScore] = useState<number | null>(null);
  const [allComplete, setAllComplete] = useState(false);

  useEffect(() => {
    let currentStep = 0;

    const interval = setInterval(() => {
      if (currentStep < steps.length) {
        setSteps(prev => 
          prev.map((step, index) => {
            if (index < currentStep) return { ...step, status: "complete" };
            if (index === currentStep) return { ...step, status: "processing" };
            return step;
          })
        );
        currentStep++;
      } else {
        clearInterval(interval);
        // Generate quality score between 75-95
        const score = Math.floor(Math.random() * 21) + 75;
        setQualityScore(score);
        setTimeout(() => setAllComplete(true), 500);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">AutoRAG OS</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12 max-w-2xl">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-2">Building {assistantName}</h1>
          <p className="text-muted-foreground">
            Processing {fileCount} file{fileCount !== 1 ? 's' : ''}...
          </p>
        </div>

        {/* Progress Steps */}
        <div className="space-y-4 mb-12">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`
                flex items-center gap-4 p-4 rounded-lg border transition-all
                ${step.status === "complete" 
                  ? "border-success bg-success/5" 
                  : step.status === "processing"
                  ? "border-primary bg-primary/5"
                  : "border-border bg-card"
                }
              `}
            >
              <div className="shrink-0">
                {step.status === "complete" && (
                  <div className="h-6 w-6 rounded-full bg-success flex items-center justify-center">
                    <Check className="h-4 w-4 text-success-foreground" />
                  </div>
                )}
                {step.status === "processing" && (
                  <Loader2 className="h-6 w-6 text-primary animate-spin" />
                )}
                {step.status === "pending" && (
                  <div className="h-6 w-6 rounded-full border-2 border-muted" />
                )}
              </div>
              <span className={`font-medium ${step.status === "pending" ? "text-muted-foreground" : ""}`}>
                {step.label}
              </span>
            </div>
          ))}
        </div>

        {/* Quality Score */}
        {qualityScore !== null && (
          <div className="text-center mb-8 animate-in fade-in duration-500">
            <div className="inline-block p-8 bg-gradient-primary rounded-2xl text-white shadow-glow">
              <p className="text-sm font-medium mb-2">RAG Quality Score</p>
              <p className="text-5xl font-bold">{qualityScore}%</p>
            </div>
          </div>
        )}

        {/* Action Button */}
        {allComplete && (
          <div className="text-center animate-in fade-in duration-500">
            <Button
              variant="hero"
              size="lg"
              onClick={() => navigate("/chat", { state: { assistantName, qualityScore } })}
              className="text-lg px-8"
            >
              Start Chatting with {assistantName}
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};

export default Processing;
