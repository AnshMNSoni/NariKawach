import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Shield,
  User,
  Phone,
  MapPin,
  Check,
  ArrowRight,
  ArrowLeft
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { z } from "zod";
import { api } from "@/lib/api";

const guardianSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, { message: "Name is required" })
    .max(100, { message: "Name is too long" }),
  phone: z
    .string()
    .trim()
    .min(10, { message: "Please enter a valid phone number" })
    .max(20, { message: "Phone number is too long" }),
});

const Onboarding = () => {
  const [step, setStep] = useState(1);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("nk_user") || "null");
    if (!user) {
      navigate("/auth");
    } else {
      setUserId(user.id);
    }
  }, [navigate]);

  const handleSaveGuardian = async () => {
    const validation = guardianSchema.safeParse({ name, phone });
    if (!validation.success) {
      toast({
        title: "Validation Error",
        description: validation.error.errors[0].message,
        variant: "destructive",
      });
      return;
    }

    if (!userId) return;

    setLoading(true);
    try {
      await api.post("/guardian/add", {
        user_id: userId,
        name: name.trim(),
        phone: phone.trim(),
      });

      setStep(2);
    } catch {
      toast({
        title: "Error",
        description: "Failed to save guardian. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFinishSetup = () => {
    toast({
      title: "Setup Complete",
      description: "Welcome to NariKawach. Stay safe!",
    });
    navigate("/home");
  };

  return (
    <div className="min-h-screen gradient-hero flex flex-col">
      {/* Header */}
      <nav className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Shield className="w-5 h-5 text-primary" />
          </div>
          <span className="text-xl font-semibold">NariKawach</span>
        </div>
      </nav>

      {/* Progress */}
      <div className="container mx-auto px-4 py-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-center gap-3 mb-2">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                step >= 1
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {step > 1 ? <Check className="w-5 h-5" /> : "1"}
            </div>
            <div
              className={`h-1 w-16 rounded-full ${
                step > 1 ? "bg-primary" : "bg-muted"
              }`}
            />
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                step >= 2
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {step > 2 ? <Check className="w-5 h-5" /> : "2"}
            </div>
          </div>
          <p className="text-center text-sm text-muted-foreground">
            Step {step} of 2
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-4 pb-12">
        <div className="w-full max-w-md animate-fade-in">
          {step === 1 ? (
            <div className="bg-card rounded-2xl p-8 border shadow-soft">
              <div className="text-center mb-8">
                <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <User className="w-7 h-7 text-primary" />
                </div>
                <h1 className="text-2xl font-semibold mb-2">
                  Add Emergency Guardian
                </h1>
                <p className="text-sm text-muted-foreground">
                  This person will be notified in case of an emergency
                </p>
              </div>

              <div className="space-y-5">
                <div>
                  <Label>Guardian Name</Label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="h-12"
                  />
                </div>

                <div>
                  <Label>Phone Number</Label>
                  <Input
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="h-12"
                  />
                </div>

                <Button
                  onClick={handleSaveGuardian}
                  disabled={loading || !name || !phone}
                  className="w-full h-12"
                >
                  {loading ? "Saving..." : "Continue"}
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </div>
            </div>
          ) : (
            <div className="bg-card rounded-2xl p-8 border shadow-soft">
              <div className="text-center mb-8">
                <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <MapPin className="w-7 h-7 text-primary" />
                </div>
                <h1 className="text-2xl font-semibold mb-2">
                  Location Consent
                </h1>
                <p className="text-sm text-muted-foreground">
                  Understanding how we use location data
                </p>
              </div>

              <Button onClick={handleFinishSetup} className="w-full h-12">
                Finish Setup
                <Check className="ml-2 w-5 h-5" />
              </Button>

              <Button
                variant="ghost"
                onClick={() => setStep(1)}
                className="w-full mt-3"
              >
                <ArrowLeft className="mr-2 w-4 h-4" />
                Go Back
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
