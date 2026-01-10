import { LucideIcon } from "lucide-react";

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  variant?: "default" | "safe" | "monitoring" | "emergency";
}

const FeatureCard = ({ icon: Icon, title, description, variant = "default" }: FeatureCardProps) => {
  const variantConfig = {
    default: {
      iconBg: "bg-primary/10",
      iconColor: "text-primary",
    },
    safe: {
      iconBg: "bg-safe/10",
      iconColor: "text-safe",
    },
    monitoring: {
      iconBg: "bg-monitoring/10",
      iconColor: "text-monitoring",
    },
    emergency: {
      iconBg: "bg-emergency/10",
      iconColor: "text-emergency",
    },
  };

  const config = variantConfig[variant];

  return (
    <div className="group relative bg-card rounded-2xl p-5 border border-border/50 shadow-soft hover:shadow-calm transition-all duration-300 hover:-translate-y-1">
      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative z-10">
        <div className={`${config.iconBg} w-12 h-12 rounded-xl flex items-center justify-center mb-4`}>
          <Icon className={`w-6 h-6 ${config.iconColor}`} />
        </div>
        <h3 className="font-display font-semibold text-foreground mb-1">{title}</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
      </div>
    </div>
  );
};

export default FeatureCard;
