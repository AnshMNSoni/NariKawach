import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Shield, Play, Square, AlertTriangle, CheckCircle, Eye, ShieldAlert, MapPin, Users, Clock, Phone, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import BottomNav from "@/components/BottomNav";
import ConfirmDialog from "@/components/ConfirmDialog";
import LocationMap from "@/components/LocationMap";
import DemoModePanel from "@/components/DemoModePanel";
import Logo from "@/components/Logo";
import FeatureCard from "@/components/FeatureCard";
import heroBanner from "@/assets/hero-banner.png";

type RiskLevel = "low" | "medium" | "high";
type SafetyStatus = "safe" | "monitoring" | "emergency";

const Home = () => {
  const [isTripActive, setIsTripActive] = useState(false);
  const [currentTripId, setCurrentTripId] = useState<string | null>(null);
  const [riskLevel, setRiskLevel] = useState<RiskLevel>("low");
  const [riskReason, setRiskReason] = useState<string>("");
  const [safetyStatus, setSafetyStatus] = useState<SafetyStatus>("safe");
  const [loading, setLoading] = useState(true);
  const [endTripDialogOpen, setEndTripDialogOpen] = useState(false);
  const [panicDialogOpen, setPanicDialogOpen] = useState(false);
  const [triggeringPanic, setTriggeringPanic] = useState(false);
  const [searchParams] = useSearchParams();
  const isDemoMode = searchParams.get("demo") === "true";
  const navigate = useNavigate();
  const { toast } = useToast();

  // Handle demo mode risk changes
  const handleDemoRiskChange = (level: RiskLevel) => {
    setRiskLevel(level);
    if (level === "high") {
      setSafetyStatus("emergency");
    } else if (level === "medium") {
      setSafetyStatus("monitoring");
    } else {
      setSafetyStatus(isTripActive ? "monitoring" : "safe");
    }
  };

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (!session?.user) {
        navigate("/auth");
      } else {
        fetchRiskStatus(session.user.id);
        checkActiveTrip(session.user.id);
      }
    });

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session?.user) {
        navigate("/auth");
      } else {
        fetchRiskStatus(session.user.id);
        checkActiveTrip(session.user.id);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  useEffect(() => {
    if (riskLevel === "high") {
      navigate("/emergency");
    }
  }, [riskLevel, navigate]);

  const checkActiveTrip = async (userId: string) => {
    const { data } = await supabase
      .from("trips")
      .select("id")
      .eq("user_id", userId)
      .eq("status", "active")
      .maybeSingle();

    if (data) {
      setIsTripActive(true);
      setCurrentTripId(data.id);
      setSafetyStatus("monitoring");
    }
  };

  const fetchRiskStatus = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from("risk_status")
        .select("*")
        .eq("user_id", userId)
        .maybeSingle();

      if (data) {
        setRiskLevel(data.risk_level as RiskLevel);
        setRiskReason(data.reason || "");
        
        if (data.risk_level === "high") {
          setSafetyStatus("emergency");
        } else if (data.risk_level === "medium") {
          setSafetyStatus("monitoring");
        } else {
          setSafetyStatus("safe");
        }
      }
    } catch (error) {
      console.error("Error fetching risk status");
    } finally {
      setLoading(false);
    }
  };

  const startTrip = async () => {
    const session = await supabase.auth.getSession();
    if (!session.data.session?.user) return;

    const { data, error } = await supabase
      .from("trips")
      .insert({
        user_id: session.data.session.user.id,
        status: "active",
      })
      .select()
      .single();

    if (data) {
      setCurrentTripId(data.id);
      setIsTripActive(true);
      setSafetyStatus("monitoring");
      toast({
        title: "Trip Started",
        description: "Safety monitoring is now active.",
      });
    }
  };

  const endTrip = async () => {
    const session = await supabase.auth.getSession();
    if (!session.data.session?.user || !currentTripId) return;

    await supabase
      .from("trips")
      .update({
        status: "completed",
        ended_at: new Date().toISOString(),
        end_risk_level: riskLevel,
      })
      .eq("id", currentTripId);

    await supabase
      .from("risk_status")
      .update({ risk_level: "low", reason: "Trip ended safely" })
      .eq("user_id", session.data.session.user.id);

    setIsTripActive(false);
    setCurrentTripId(null);
    setSafetyStatus("safe");
    setRiskLevel("low");
    setEndTripDialogOpen(false);

    toast({
      title: "Trip Ended",
      description: "Safety monitoring has been stopped.",
    });
  };

  const handleTripToggle = () => {
    if (isTripActive) {
      setEndTripDialogOpen(true);
    } else {
      startTrip();
    }
  };

  const triggerPanic = async () => {
    setTriggeringPanic(true);
    try {
      const session = await supabase.auth.getSession();
      if (!session.data.session?.user) return;

      const userId = session.data.session.user.id;

      const { data: existingStatus } = await supabase
        .from("risk_status")
        .select("id")
        .eq("user_id", userId)
        .maybeSingle();

      if (existingStatus) {
        await supabase
          .from("risk_status")
          .update({ 
            risk_level: "high", 
            reason: "Panic button activated" 
          })
          .eq("user_id", userId);
      } else {
        await supabase
          .from("risk_status")
          .insert({ 
            user_id: userId,
            risk_level: "high", 
            reason: "Panic button activated" 
          });
      }

      if (!isTripActive) {
        const { data } = await supabase
          .from("trips")
          .insert({
            user_id: userId,
            status: "active",
          })
          .select()
          .single();

        if (data) {
          setCurrentTripId(data.id);
          setIsTripActive(true);
        }
      }

      setRiskLevel("high");
      setSafetyStatus("emergency");
      setPanicDialogOpen(false);
    } catch (error) {
      console.error("Error triggering panic:", error);
      toast({
        title: "Error",
        description: "Failed to trigger emergency. Please try again.",
        variant: "destructive",
      });
    } finally {
      setTriggeringPanic(false);
    }
  };

  const getStatusConfig = () => {
    switch (safetyStatus) {
      case "safe":
        return {
          gradient: "from-safe/5 via-safe/10 to-transparent",
          icon: CheckCircle,
          iconColor: "text-safe",
          label: "All Clear",
          description: "You're protected. Start a trip when you're ready.",
          pulse: false,
        };
      case "monitoring":
        return {
          gradient: "from-monitoring/5 via-monitoring/10 to-transparent",
          icon: Eye,
          iconColor: "text-monitoring",
          label: "Monitoring Active",
          description: "Your guardians are watching over you.",
          pulse: true,
        };
      case "emergency":
        return {
          gradient: "from-emergency/5 via-emergency/10 to-transparent",
          icon: AlertTriangle,
          iconColor: "text-emergency",
          label: "Emergency Mode",
          description: "Help is on the way.",
          pulse: true,
        };
    }
  };

  const getRiskBadgeConfig = () => {
    switch (riskLevel) {
      case "low":
        return { bg: "bg-safe", text: "text-safe-foreground", label: "Low Risk" };
      case "medium":
        return { bg: "bg-monitoring", text: "text-monitoring-foreground", label: "Medium Risk" };
      case "high":
        return { bg: "bg-emergency", text: "text-emergency-foreground", label: "High Risk" };
    }
  };

  const statusConfig = getStatusConfig();
  const riskConfig = getRiskBadgeConfig();
  const StatusIcon = statusConfig.icon;

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Logo size="lg" />
          <div className="flex items-center gap-2 mt-4">
            <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
            <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
            <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Navigation Bar */}
      <header className="relative z-50 border-b border-border/50 bg-background/95 backdrop-blur-lg sticky top-0">
        <nav className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <Logo size="sm" />
            <div className="flex items-center gap-3">
              <div className={`${riskConfig.bg} ${riskConfig.text} px-3 py-1.5 rounded-full text-xs font-semibold shadow-sm flex items-center gap-1.5`}>
                <div className={`w-1.5 h-1.5 rounded-full ${riskLevel === 'low' ? 'bg-white' : 'bg-white/80'} ${riskLevel !== 'low' ? 'animate-pulse' : ''}`} />
                {riskConfig.label}
              </div>
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section with Full-Width Banner */}
      {!isTripActive && (
        <section className="relative overflow-hidden">
          {/* Hero Image with Diagonal Overlay */}
          <div className="relative h-64 md:h-80 w-full">
            <img 
              src={heroBanner}
              alt="NariKawach Protection"
              className="w-full h-full object-cover"
            />
            {/* Diagonal overlay effect like Fortis */}
            <div className="absolute inset-0 bg-gradient-to-r from-background/90 via-background/50 to-transparent" />
            <div className="absolute inset-0" style={{
              background: 'linear-gradient(135deg, transparent 40%, hsl(var(--background) / 0.95) 100%)'
            }} />
            
            {/* Hero Content */}
            <div className="absolute inset-0 flex items-center">
              <div className="container mx-auto px-4">
                <div className="max-w-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <StatusIcon className={`w-5 h-5 ${statusConfig.iconColor} ${statusConfig.pulse ? 'animate-pulse' : ''}`} />
                    <span className={`text-sm font-semibold ${statusConfig.iconColor}`}>
                      {statusConfig.label}
                    </span>
                  </div>
                  <h1 className="text-3xl md:text-4xl font-display font-bold text-foreground mb-2">
                    Safety for Every Journey
                  </h1>
                  <p className="text-base text-muted-foreground max-w-md">
                    Real-time protection and instant guardian alerts when you need them most.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Main Content */}
      <main className={`flex-1 relative z-10 ${!isTripActive ? '-mt-6' : 'pt-4'} pb-28`}>
        <div className="container mx-auto px-4">
          
          {/* Quick Action Cards - When not tracking */}
          {!isTripActive && (
            <section className="mb-6">
              <div className="grid grid-cols-2 gap-4">
                <FeatureCard
                  icon={MapPin}
                  title="Live Tracking"
                  description="Share your real-time location with guardians"
                  variant="default"
                />
                <FeatureCard
                  icon={Users}
                  title="Guardian Network"
                  description="Trusted contacts always watching over you"
                  variant="safe"
                />
                <FeatureCard
                  icon={Bell}
                  title="Smart Alerts"
                  description="Automatic notifications for unusual activity"
                  variant="monitoring"
                />
                <FeatureCard
                  icon={Phone}
                  title="Quick Response"
                  description="One-tap emergency assistance"
                  variant="emergency"
                />
              </div>
            </section>
          )}

          {/* Active Trip Content */}
          {isTripActive && (
            <section className="mb-6 animate-fade-in">
              <div className={`bg-gradient-to-br ${statusConfig.gradient} rounded-3xl p-6 border border-border/30 shadow-soft`}>
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-16 h-16 rounded-2xl bg-card flex items-center justify-center shadow-sm ${statusConfig.pulse ? 'animate-pulse' : ''}`}>
                    <StatusIcon className={`w-8 h-8 ${statusConfig.iconColor}`} />
                  </div>
                  <div>
                    <h2 className="text-2xl font-display font-bold text-foreground">
                      {statusConfig.label}
                    </h2>
                    <p className="text-sm text-muted-foreground">
                      {statusConfig.description}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 px-4 py-2.5 bg-card/50 rounded-xl border border-border/30">
                  <div className="w-2 h-2 rounded-full bg-safe animate-pulse" />
                  <span className="text-sm text-muted-foreground">Live tracking enabled • Guardians notified</span>
                </div>
              </div>
            </section>
          )}

          {/* Medium Risk Warning */}
          {riskLevel === "medium" && (
            <section className="mb-6 animate-slide-up">
              <div className="bg-gradient-to-r from-monitoring/10 to-monitoring/5 rounded-2xl p-5 border border-monitoring/20">
                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-monitoring/20 flex items-center justify-center flex-shrink-0">
                    <AlertTriangle className="w-6 h-6 text-monitoring" />
                  </div>
                  <div>
                    <h3 className="font-display font-semibold text-foreground mb-1">
                      Stay Alert
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      You appear to be in an unfamiliar area. Your guardians have been notified.
                    </p>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Map Section */}
          <section className="mb-6">
            <div className="rounded-3xl overflow-hidden shadow-soft border border-border/50">
              <LocationMap isTracking={isTripActive} />
            </div>
          </section>

          {/* Action Buttons */}
          <section className="space-y-4">
            <Button
              onClick={handleTripToggle}
              size="lg"
              className={`w-full h-16 text-base font-semibold rounded-2xl shadow-calm transition-all duration-300 ${
                isTripActive
                  ? "bg-gradient-to-r from-destructive to-destructive/80 hover:from-destructive/90 hover:to-destructive/70"
                  : "bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
              }`}
            >
              {isTripActive ? (
                <>
                  <Square className="w-5 h-5 mr-3" />
                  End Trip Safely
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-3" />
                  Start Protected Trip
                </>
              )}
            </Button>
            
            <p className="text-xs text-center text-muted-foreground px-4">
              {isTripActive
                ? "Tap to end your trip and mark yourself as safe"
                : "Your location will be monitored and shared with guardians"}
            </p>

            {/* Emergency SOS Button */}
            <Button
              onClick={() => setPanicDialogOpen(true)}
              variant="outline"
              className="w-full h-14 text-base font-bold rounded-2xl border-2 border-emergency/40 bg-gradient-to-r from-emergency/5 to-emergency/10 text-emergency hover:from-emergency hover:to-emergency/90 hover:text-white hover:border-emergency transition-all duration-300 shadow-sm"
            >
              <ShieldAlert className="w-5 h-5 mr-3" />
              Emergency SOS
            </Button>
            <p className="text-xs text-center text-muted-foreground">
              Instantly alert all guardians
            </p>
          </section>
        </div>
      </main>

      {isDemoMode && (
        <DemoModePanel
          onRiskChange={handleDemoRiskChange}
          currentRisk={riskLevel}
          isTripActive={isTripActive}
        />
      )}

      <BottomNav />

      <ConfirmDialog
        open={endTripDialogOpen}
        onOpenChange={setEndTripDialogOpen}
        title="End Trip?"
        description="This will stop safety monitoring and mark you as arrived safely. Your guardians will be notified."
        confirmText="End Trip"
        onConfirm={endTrip}
      />

      <ConfirmDialog
        open={panicDialogOpen}
        onOpenChange={setPanicDialogOpen}
        title="Trigger Emergency?"
        description="This will immediately alert all your guardians and activate emergency protocols. Only use this in a real emergency."
        confirmText={triggeringPanic ? "Triggering..." : "Trigger Emergency"}
        onConfirm={triggerPanic}
        variant="destructive"
      />
    </div>
  );
};

export default Home;
