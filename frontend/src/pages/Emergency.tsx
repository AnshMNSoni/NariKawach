import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, MapPin, Phone, CheckCircle, User, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";

interface Guardian {
  id: string;
  name: string;
  phone: string;
}

const Emergency = () => {
  const [guardians, setGuardians] = useState<Guardian[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (!session?.user) {
        navigate("/auth");
      } else {
        fetchGuardians(session.user.id);
      }
    });

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session?.user) {
        navigate("/auth");
      } else {
        fetchGuardians(session.user.id);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const fetchGuardians = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from("guardians")
        .select("*")
        .eq("user_id", userId);

      if (data) {
        setGuardians(data);
      }
    } catch (error) {
      console.error("Error fetching guardians");
    } finally {
      setLoading(false);
    }
  };

  const handleReturnHome = async () => {
    const session = await supabase.auth.getSession();
    if (session.data.session?.user) {
      // Reset risk level when leaving emergency
      await supabase
        .from("risk_status")
        .update({ risk_level: "low", reason: "Emergency resolved" })
        .eq("user_id", session.data.session.user.id);
    }
    navigate("/home");
  };

  if (loading) {
    return (
      <div className="min-h-screen gradient-emergency flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-emergency/30 border-t-emergency rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-emergency flex flex-col">
      {/* Header */}
      <nav className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-emergency/10 flex items-center justify-center">
            <Shield className="w-5 h-5 text-emergency" />
          </div>
          <span className="text-xl font-semibold text-foreground">NariKawach</span>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-4 py-6">
        <div className="max-w-lg mx-auto space-y-6">
          {/* Emergency Banner */}
          <div className="bg-card rounded-2xl p-6 shadow-soft border border-emergency/20 animate-fade-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-emergency/10 flex items-center justify-center">
                <Shield className="w-6 h-6 text-emergency animate-pulse-soft" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">
                  Emergency Mode Active
                </h1>
                <p className="text-sm text-muted-foreground">
                  Safety protocols initiated
                </p>
              </div>
            </div>

            {/* SOS Status */}
            <div className="flex items-center gap-2 px-4 py-3 bg-emergency/5 rounded-xl border border-emergency/10">
              <CheckCircle className="w-5 h-5 text-emergency" />
              <span className="text-sm font-medium text-foreground">
                SOS Sent — Your contacts have been notified
              </span>
            </div>
          </div>

          {/* Location Card */}
          <div className="bg-card rounded-2xl overflow-hidden shadow-soft border border-border/50">
            <div className="p-4 border-b border-border">
              <h2 className="font-medium text-foreground flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emergency" />
                Live Location Sharing
              </h2>
            </div>
            <div className="aspect-[16/9] bg-gradient-to-br from-emergency/5 to-accent relative">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-emergency/10 flex items-center justify-center mx-auto mb-3 animate-pulse-soft">
                    <MapPin className="w-8 h-8 text-emergency" />
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Location is being shared with your guardians
                  </p>
                </div>
              </div>
              {/* Simulated map grid */}
              <div className="absolute inset-0 opacity-10">
                <div className="w-full h-full" style={{
                  backgroundImage: "linear-gradient(hsl(var(--emergency) / 0.2) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--emergency) / 0.2) 1px, transparent 1px)",
                  backgroundSize: "40px 40px"
                }} />
              </div>
            </div>
          </div>

          {/* Guardian Contacts */}
          <div className="bg-card rounded-2xl shadow-soft border border-border/50">
            <div className="p-4 border-b border-border">
              <h2 className="font-medium text-foreground">
                Emergency Contacts Notified
              </h2>
            </div>
            <div className="p-4 space-y-3">
              {guardians.length > 0 ? (
                guardians.map((guardian) => (
                  <div
                    key={guardian.id}
                    className="flex items-center justify-between p-3 bg-accent/30 rounded-xl"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{guardian.name}</p>
                        <p className="text-sm text-muted-foreground">{guardian.phone}</p>
                      </div>
                    </div>
                    <a
                      href={`tel:${guardian.phone}`}
                      className="w-10 h-10 rounded-full bg-safe flex items-center justify-center hover:bg-safe/90 transition-colors"
                    >
                      <Phone className="w-5 h-5 text-safe-foreground" />
                    </a>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No guardians configured
                </p>
              )}
            </div>
          </div>

          {/* Return Button */}
          <Button
            onClick={handleReturnHome}
            variant="outline"
            className="w-full h-12 text-base"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Return to Dashboard
          </Button>

          <p className="text-xs text-center text-muted-foreground">
            Stay calm. Help is on the way.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Emergency;
