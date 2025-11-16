import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useNavigate } from "react-router-dom";
import { Upload, FileText, Image, Music, X, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface UploadedFile {
  name: string;
  type: string;
  size: number;
}

const WorkspaceSetup = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [assistantName, setAssistantName] = useState("");
  const [description, setDescription] = useState("");
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const getFileIcon = (type: string) => {
    if (type.includes("pdf")) return FileText;
    if (type.includes("image")) return Image;
    if (type.includes("audio")) return Music;
    return FileText;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  };

  const addFiles = (newFiles: File[]) => {
    const fileData = newFiles.map(f => ({
      name: f.name,
      type: f.type,
      size: f.size
    }));
    setFiles(prev => [...prev, ...fileData]);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (!assistantName.trim()) {
      toast({
        title: "Name required",
        description: "Please give your assistant a name",
        variant: "destructive"
      });
      return;
    }

    if (files.length === 0) {
      toast({
        title: "Files required",
        description: "Please upload at least one file",
        variant: "destructive"
      });
      return;
    }

    navigate("/processing", { 
      state: { 
        assistantName, 
        description, 
        fileCount: files.length 
      } 
    });
  };

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
      <main className="container mx-auto px-4 py-12 max-w-3xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Create Your Assistant</h1>
          <p className="text-muted-foreground">
            Upload your documents and we'll build a custom AI assistant for you
          </p>
        </div>

        {/* Assistant Details */}
        <div className="space-y-6 mb-8">
          <div>
            <Label htmlFor="name">Assistant Name *</Label>
            <Input
              id="name"
              placeholder="e.g., HR Policies Assistant"
              value={assistantName}
              onChange={(e) => setAssistantName(e.target.value)}
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea
              id="description"
              placeholder="What will this assistant help with?"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="mt-2"
              rows={3}
            />
          </div>
        </div>

        {/* File Upload Zone */}
        <div className="mb-6">
          <Label>Upload Files *</Label>
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              mt-2 border-2 border-dashed rounded-lg p-12 text-center transition-colors
              ${isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
            `}
          >
            <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-lg font-medium mb-2">Drop files here or click to browse</p>
            <p className="text-sm text-muted-foreground mb-4">
              Supports: PDF, PNG, JPG, MP3, DOCX
            </p>
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              className="hidden"
              id="file-input"
              accept=".pdf,.png,.jpg,.jpeg,.mp3,.docx"
            />
            <Button variant="outline" onClick={() => document.getElementById('file-input')?.click()}>
              Select Files
            </Button>
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="space-y-3 mb-8">
            <Label>Uploaded Files ({files.length})</Label>
            {files.map((file, index) => {
              const Icon = getFileIcon(file.type);
              return (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 border border-border rounded-lg bg-card"
                >
                  <Icon className="h-5 w-5 text-primary shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{file.name}</p>
                    <p className="text-sm text-muted-foreground">{formatFileSize(file.size)}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              );
            })}
          </div>
        )}

        {/* Submit Button */}
        <Button
          variant="hero"
          size="lg"
          className="w-full"
          onClick={handleSubmit}
        >
          Process Files and Build Assistant
        </Button>
      </main>
    </div>
  );
};

export default WorkspaceSetup;
