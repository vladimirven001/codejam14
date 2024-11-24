import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";
import { useState, useEffect } from "react";

const Index = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
      const currentUser = localStorage.getItem("currentUser");
      if (currentUser) {
          try {
              const user = JSON.parse(currentUser);
              if (user && user.id && user.email) {
                  setIsLoggedIn(true); // User is logged in
              } else {
                  setIsLoggedIn(false); // Invalid user data
                  localStorage.removeItem("currentUser"); // Clean up invalid data
              }
          } catch (error) {
              console.error("Error parsing user data:", error);
              setIsLoggedIn(false);
              localStorage.removeItem("currentUser");
          }
      } else {
          setIsLoggedIn(false); // No user found
      }
  }, []); // Run this only once when the component mounts

/*   // Optional: Redirect to login if not logged in
  useEffect(() => {
      if (!isLoggedIn) {
          navigate("/auth/login");
      }
  }, [isLoggedIn, navigate]); */

  const handleAuthAction = () => {
    if (isLoggedIn) {
      navigate("/chat");
    } else {
      navigate("/auth/signup");
      toast({
        title: "Welcome!",
        description: "Create an account to start uploading your notes.",
      });
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-6xl space-y-16">
        {/* Hero Section */}
        <section className="text-center space-y-6 fade-up">
          <div className="space-y-2">
            <div className="inline-block">
              <span className="px-3 py-1 text-sm font-medium bg-primary/10 text-primary rounded-full">
                Beta Release
              </span>
            </div>
            <h1 className="text-4xl sm:text-6xl font-display font-bold tracking-tight">
              Your Class Notes,{" "}
              <span className="text-primary">Supercharged with AI</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Transform your study materials into an intelligent knowledge base.
              Upload your notes and get instant, contextual answers powered by AI.
            </p>
          </div>
          
          <div className="flex justify-center items-center">
            <Button
              size="lg"
              className="hover-scale"
              onClick={handleAuthAction}
            >
              {isLoggedIn ? "Upload Your Notes" : "Create Account"}
            </Button>
          </div>
        </section>

        {/* Features Grid */}
        <section className="grid md:grid-cols-3 gap-6 fade-up" style={{ animationDelay: "200ms" }}>
          <FeatureCard
            title="Smart Context"
            description="Our AI understands your notes and provides relevant answers based on your course material."
          />
          <FeatureCard
            title="Easy Upload"
            description="Support for PDF, Word, and text files. Just drag and drop your study materials."
          />
          <FeatureCard
            title="Quick Answers"
            description="Get instant, accurate responses to your questions, sourced directly from your notes."
          />
        </section>
      </div>
    </div>
  );
};

const FeatureCard = ({ title, description }: { title: string; description: string }) => (
  <Card className="p-6 glass-card hover-scale">
    <h3 className="text-xl font-display font-semibold mb-2">{title}</h3>
    <p className="text-muted-foreground">{description}</p>
  </Card>
);

export default Index;