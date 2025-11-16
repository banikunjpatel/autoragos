import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Sparkles, FileText, MessageSquare, BarChart3, Upload } from "lucide-react";

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Upload,
      title: "Drop Any File",
      description: "PDFs, images, audio, emails - we handle the mess"
    },
    {
      icon: FileText,
      title: "Auto-Processing",
      description: "OCR, transcription, and chunking done automatically"
    },
    {
      icon: MessageSquare,
      title: "Instant Chat",
      description: "Ask questions and get answers with confidence scores"
    },
    {
      icon: BarChart3,
      title: "Quality Scores",
      description: "Know exactly how reliable your assistant is"
    }
  ];

  const partners = [
    { name: "Gemini", logo: "✨" },
    { name: "Qdrant", logo: "🔷" },
    { name: "Opus", logo: "🎵" },
    { name: "AIML API", logo: "🤖" }
  ];

  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Header */}
      <header className="border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AutoRAG OS</span>
          </div>
          <Button variant="outline" onClick={() => navigate("/workspace")}>
            Sign In
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
            Upload your world.<br />
            Get your own AI assistant.
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-2xl mx-auto">
            AutoRAG OS lets you drop in your documents and instantly chat with your knowledge.
          </p>
          <Button 
            variant="hero" 
            size="lg"
            onClick={() => navigate("/workspace")}
            className="text-lg px-8 py-6 h-auto"
          >
            Create Your RAG Assistant
          </Button>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <feature.icon className="h-10 w-10 text-primary mb-4" />
              <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-muted-foreground text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Partners Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-sm text-muted-foreground mb-6">Powered by industry-leading AI technology</p>
          <div className="flex justify-center items-center gap-12 flex-wrap">
            {partners.map((partner, index) => (
              <div key={index} className="flex items-center gap-2 text-lg opacity-60 hover:opacity-100 transition-opacity">
                <span className="text-2xl">{partner.logo}</span>
                <span className="font-semibold">{partner.name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-muted-foreground">
          <p>© 2025 AutoRAG OS. Built for knowledge workers who need AI that works.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
