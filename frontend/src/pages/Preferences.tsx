import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, ArrowLeft, Gauge, Bell, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import BottomNav from "@/components/BottomNav";

type SensitivityLevel = "conservative" | "balanced" | "alert";

const Preferences = () => {
  const [sensitivity, setSensitivity] = useState<SensitivityLevel>("balanced");
  const [autoSuggest, setAutoSuggest] = useState(true);
  const [saved, setSaved] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) {
        navigate("/auth");
      }
    };
    checkAuth();

    // Load from localStorage
    const savedSensitivity = localStorage.getItem("safety_sensitivity") as SensitivityLevel;
    const savedAutoSuggest = localStorage.getItem("auto_suggest");
    if (savedSensitivity) setSensitivity(savedSensitivity);
    if (savedAutoSuggest !== null) setAutoSuggest(savedAutoSuggest === "true");
  }, [navigate]);

  const handleSave = () => {
    localStorage.setItem("safety_sensitivity", sensitivity);
    localStorage.setItem("auto_suggest", String(autoSuggest));
    setSaved(true);
    toast({ title: "Preferences Saved", description: "Your safety preferences have been updated." });
    setTimeout(() => setSaved(false), 2000);
  };

  const sensitivityOptions = [
    {
      value: "conservative" as const,
      label: "Conservative",
      description: "Fewer alerts, only notify for clear risks",
      icon: "🛡️",
    },
    {
      value: "balanced" as const,
      label: "Balanced",
      description: "Recommended setting for most users",
      icon: "⚖️",
    },
    {
      value: "alert" as const,
      label: "Alert",
      description: "More frequent alerts, extra cautious",
      icon: "🔔",
    },
  ];

  return (
    <div className="min-h-screen gradient-hero flex flex-col pb-24">
      {/* Header */}
      <nav className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate("/settings")}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Gauge className="w-5 h-5 text-primary" />
            </div>
            <span className="text-xl font-semibold text-foreground">Safety Preferences</span>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1 container mx-auto px-4 py-4">
        <div className="max-w-lg mx-auto space-y-6">
          {/* Sensitivity Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 p-5 animate-fade-in">
            <h2 className="text-lg font-semibold text-foreground mb-2 flex items-center gap-2">
              <Gauge className="w-5 h-5 text-primary" />
              Safety Sensitivity
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              Choose how sensitive the safety detection should be.
            </p>

            <div className="space-y-3">
              {sensitivityOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setSensitivity(option.value)}
                  className={`w-full p-4 rounded-xl border transition-all text-left flex items-start gap-3 ${
                    sensitivity === option.value
                      ? "bg-primary/5 border-primary/30"
                      : "bg-muted/30 border-transparent hover:border-border"
                  }`}
                >
                  <span className="text-2xl">{option.icon}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-foreground">{option.label}</p>
                      {sensitivity === option.value && (
                        <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                          <Check className="w-3 h-3 text-primary-foreground" />
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{option.description}</p>
                  </div>
                </button>
              ))}
            </div>
          </section>

          {/* Auto-Suggest Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 p-5 animate-fade-in">
            <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary" />
              Suggestions
            </h2>

            <div className="flex items-center justify-between p-4 bg-muted/30 rounded-xl">
              <div>
                <p className="font-medium text-foreground">Auto-Suggest Safety Actions</p>
                <p className="text-sm text-muted-foreground">
                  Show contextual safety tips and suggestions
                </p>
              </div>
              <Switch checked={autoSuggest} onCheckedChange={setAutoSuggest} />
            </div>
          </section>

          {/* Save Button */}
          <Button onClick={handleSave} className="w-full h-12 text-base shadow-calm">
            {saved ? (
              <>
                <Check className="w-5 h-5 mr-2" />
                Saved!
              </>
            ) : (
              "Save Preferences"
            )}
          </Button>

          <p className="text-xs text-center text-muted-foreground">
            Preferences are stored locally on your device.
          </p>
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default Preferences;
