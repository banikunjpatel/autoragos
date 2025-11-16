import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sparkles, MessageSquare, TrendingUp, AlertCircle } from "lucide-react";

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { assistantName = "Your Assistant", qualityScore = 81 } = location.state || {};

  const testQuestions = [
    {
      question: "What is the employee vacation policy?",
      score: 0.92,
      status: "excellent"
    },
    {
      question: "How do I request time off?",
      score: 0.88,
      status: "good"
    },
    {
      question: "What are the remote work guidelines?",
      score: 0.75,
      status: "fair"
    },
    {
      question: "What is the dress code policy?",
      score: 0.65,
      status: "needs-improvement"
    }
  ];

  const getScoreColor = (score: number) => {
    if (score >= 0.85) return "text-success";
    if (score >= 0.7) return "text-warning";
    return "text-destructive";
  };

  const getScoreLabel = (status: string) => {
    switch (status) {
      case "excellent": return "Excellent";
      case "good": return "Good";
      case "fair": return "Fair";
      case "needs-improvement": return "Needs Improvement";
      default: return "";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-primary" />
            <div>
              <h1 className="font-bold text-lg">{assistantName}</h1>
              <p className="text-sm text-muted-foreground">Quality Dashboard</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/chat", { state: { assistantName, qualityScore } })}
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Back to Chat
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Overall Score Card */}
        <div className="mb-8 bg-gradient-primary text-white rounded-2xl p-8 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90 mb-2">Overall RAG Quality Score</p>
              <p className="text-5xl font-bold">{qualityScore}%</p>
              <p className="text-sm opacity-90 mt-2">Last updated: Just now</p>
            </div>
            <div className="text-right">
              <TrendingUp className="h-12 w-12 mb-2 opacity-90" />
              <p className="text-sm opacity-90">Your assistant is performing well</p>
            </div>
          </div>
        </div>

        {/* Test Questions Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Auto-Generated Test Questions</h2>
          <p className="text-muted-foreground mb-6">
            We automatically test your assistant with questions based on your documents
          </p>

          <div className="space-y-4">
            {testQuestions.map((test, index) => (
              <div
                key={index}
                className="border border-border rounded-lg p-4 bg-card hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="font-medium mb-2">{test.question}</p>
                    <p className="text-sm text-muted-foreground">
                      Status: <span className={getScoreColor(test.score)}>{getScoreLabel(test.status)}</span>
                    </p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className={`text-2xl font-bold ${getScoreColor(test.score)}`}>
                      {(test.score * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-muted-foreground">Confidence</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Suggestions Card */}
        <div className="bg-muted/50 border border-border rounded-lg p-6">
          <div className="flex gap-3 mb-4">
            <AlertCircle className="h-5 w-5 text-primary shrink-0" />
            <div>
              <h3 className="font-semibold mb-2">Suggestions to Improve</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Upload more documents about dress code policies to improve coverage</li>
                <li>• Consider adding FAQ documents to help with common questions</li>
                <li>• Your assistant excels at vacation and time-off questions - great job!</li>
              </ul>
            </div>
          </div>
          <Button variant="outline" size="sm" className="mt-4" onClick={() => navigate("/workspace")}>
            Upload More Documents
          </Button>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
