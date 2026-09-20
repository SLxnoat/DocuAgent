import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";

interface OptionsPanelProps {
  outputFormats: ("markdown" | "html" | "pdf")[];
  onChangeFormats: (formats: ("markdown" | "html" | "pdf")[]) => void;
  language: string;
  onChangeLanguage: (lang: string) => void;
  domainHint: string;
  onChangeDomainHint: (domain: string) => void;
}

export function OptionsPanel({
  outputFormats,
  onChangeFormats,
  language,
  onChangeLanguage,
  domainHint,
  onChangeDomainHint,
}: OptionsPanelProps) {
  const toggleFormat = (format: "markdown" | "html" | "pdf") => {
    if (outputFormats.includes(format)) {
      if (outputFormats.length > 1) {
        onChangeFormats(outputFormats.filter((f) => f !== format));
      }
    } else {
      onChangeFormats([...outputFormats, format]);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-4 rounded-lg bg-muted/40 border">
      {/* Output Formats */}
      <div className="flex flex-col gap-2">
        <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Export Formats
        </Label>
        <div className="flex items-center gap-4 pt-1">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="fmt-md"
              checked={outputFormats.includes("markdown")}
              onCheckedChange={() => toggleFormat("markdown")}
            />
            <label
              htmlFor="fmt-md"
              className="text-sm font-medium leading-none cursor-pointer"
            >
              Markdown
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="fmt-html"
              checked={outputFormats.includes("html")}
              onCheckedChange={() => toggleFormat("html")}
            />
            <label
              htmlFor="fmt-html"
              className="text-sm font-medium leading-none cursor-pointer"
            >
              HTML
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="fmt-pdf"
              checked={outputFormats.includes("pdf")}
              onCheckedChange={() => toggleFormat("pdf")}
            />
            <label
              htmlFor="fmt-pdf"
              className="text-sm font-medium leading-none cursor-pointer"
            >
              PDF
            </label>
          </div>
        </div>
      </div>

      {/* Target Language */}
      <div className="flex flex-col gap-2">
        <Label
          htmlFor="lang-select"
          className="text-xs font-semibold text-muted-foreground uppercase tracking-wider"
        >
          Document Language
        </Label>
        <Select value={language} onValueChange={onChangeLanguage}>
          <SelectTrigger id="lang-select" className="h-9">
            <SelectValue placeholder="Select Language" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="en">English (US)</SelectItem>
            <SelectItem value="es">Spanish</SelectItem>
            <SelectItem value="fr">French</SelectItem>
            <SelectItem value="de">German</SelectItem>
            <SelectItem value="ja">Japanese</SelectItem>
            <SelectItem value="zh">Chinese</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Domain Context Override */}
      <div className="flex flex-col gap-2">
        <Label
          htmlFor="domain-hint"
          className="text-xs font-semibold text-muted-foreground uppercase tracking-wider"
        >
          Domain Hint (Optional)
        </Label>
        <Input
          id="domain-hint"
          placeholder="e.g. SaaS Admin, Banking, CRM"
          value={domainHint}
          onChange={(e) => onChangeDomainHint(e.target.value)}
          className="h-9"
        />
      </div>
    </div>
  );
}
