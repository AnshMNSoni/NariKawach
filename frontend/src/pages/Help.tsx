import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, HelpCircle, CheckCircle, Eye, AlertTriangle, MapPin, Lock, Camera, Mic, Users, ChevronDown, ChevronUp } from "lucide-react";
import { getUser } from "@/utils/auth";
import BottomNav from "@/components/BottomNav";

type ExpandedSections = {
  howItWorks: boolean;
  riskLevels: boolean;
  dataUsed: boolean;
  dataNotUsed: boolean;
};

const Help = () => {
  const [expanded, setExpanded] = useState<ExpandedSections>({
    howItWorks: true,
    riskLevels: true,
    dataUsed: false,
    dataNotUsed: false,
  });
  const navigate = useNavigate();

  useEffect(() => {
    const user = getUser();
    if (!user) {
      navigate("/auth");
    }
  }, [navigate]);

  const toggleSection = (section: keyof ExpandedSections) => {
    setExpanded({ ...expanded, [section]: !expanded[section] });
  };

  const SectionHeader = ({
    title,
    icon: Icon,
    section,
  }: {
    title: string;
    icon: React.ElementType;
    section: keyof ExpandedSections;
  }) => (
    <button
      onClick={() => toggleSection(section)}
      className="w-full flex items-center justify-between p-4 bg-muted/30 rounded-xl hover:bg-muted/50 transition-colors"
    >
      <div className="flex items-center gap-3">
        <Icon className="w-5 h-5 text-primary" />
        <span className="font-medium text-foreground">{title}</span>
      </div>
      {expanded[section] ? (
        <ChevronUp className="w-5 h-5 text-muted-foreground" />
      ) : (
        <ChevronDown className="w-5 h-5 text-muted-foreground" />
      )}
    </button>
  );

  return (
    <div className="min-h-screen gradient-hero flex flex-col pb-24">
      {/* Header */}
      <nav className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <HelpCircle className="w-5 h-5 text-primary" />
          </div>
          <span className="text-xl font-semibold text-foreground">Help & Transparency</span>
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1 container mx-auto px-4 py-4">
        <div className="max-w-lg mx-auto space-y-4">
          {/* Intro Card */}
          <div className="bg-card rounded-2xl shadow-soft border border-border/50 p-5 animate-fade-in">
            <div className="flex gap-3">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-foreground mb-1">
                  How NariKawach Works
                </h1>
                <p className="text-sm text-muted-foreground">
                  NariKawach is your silent safety companion. We help detect potentially unsafe situations early using contextual awareness — without surveillance.
                </p>
              </div>
            </div>
          </div>

          {/* Risk Levels Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 overflow-hidden animate-fade-in">
            <SectionHeader title="Risk Levels Explained" icon={AlertTriangle} section="riskLevels" />
            {expanded.riskLevels && (
              <div className="p-4 space-y-4 border-t border-border/30">
                <div className="flex gap-3 p-3 rounded-xl bg-safe/5 border border-safe/20">
                  <CheckCircle className="w-5 h-5 text-safe flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">Low Risk</p>
                    <p className="text-sm text-muted-foreground">
                      Everything appears normal. No concerns detected. You're in familiar territory.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 p-3 rounded-xl bg-monitoring/5 border border-monitoring/20">
                  <Eye className="w-5 h-5 text-monitoring flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">Medium Risk</p>
                    <p className="text-sm text-muted-foreground">
                      Some contextual factors suggest extra caution. You'll see suggestions but no automatic actions.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 p-3 rounded-xl bg-emergency/5 border border-emergency/20">
                  <AlertTriangle className="w-5 h-5 text-emergency flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">High Risk</p>
                    <p className="text-sm text-muted-foreground">
                      Emergency mode activates. Your guardians are notified with your location. Stay calm — help is on the way.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* Data Used Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 overflow-hidden animate-fade-in">
            <SectionHeader title="What Data We Use" icon={MapPin} section="dataUsed" />
            {expanded.dataUsed && (
              <div className="p-4 space-y-3 border-t border-border/30">
                <div className="flex gap-3 p-3 rounded-xl bg-muted/30">
                  <MapPin className="w-5 h-5 text-primary flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">Location During Trips</p>
                    <p className="text-sm text-muted-foreground">
                      Only when you start a trip. Never in the background.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 p-3 rounded-xl bg-muted/30">
                  <AlertTriangle className="w-5 h-5 text-primary flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">Risk Status</p>
                    <p className="text-sm text-muted-foreground">
                      Your current safety level based on context.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* Data NOT Used Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 overflow-hidden animate-fade-in">
            <SectionHeader title="What We Never Access" icon={Lock} section="dataNotUsed" />
            {expanded.dataNotUsed && (
              <div className="p-4 space-y-3 border-t border-border/30">
                <div className="flex gap-3 p-3 rounded-xl bg-safe/5">
                  <Camera className="w-5 h-5 text-safe flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">Camera</p>
                    <p className="text-sm text-muted-foreground">
                      We never access your camera or photos.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 p-3 rounded-xl bg-safe/5">
                  <Mic className="w-5 h-5 text-safe flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">Microphone / Audio</p>
                    <p className="text-sm text-muted-foreground">
                      We never listen to or record audio.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 p-3 rounded-xl bg-safe/5">
                  <Users className="w-5 h-5 text-safe flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">Phone Contacts</p>
                    <p className="text-sm text-muted-foreground">
                      Only guardians you manually add are stored.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* Trust Statement */}
          <div className="bg-primary/5 rounded-2xl p-5 border border-primary/20 animate-fade-in">
            <p className="text-sm text-center text-foreground">
              <strong>Your privacy is our priority.</strong> NariKawach was built with a consent-first approach. You're always in control.
            </p>
          </div>
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default Help;
