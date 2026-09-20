import React, { useState } from "react";
import {
  Sparkles,
  Lock,
  Globe,
  FileCode,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Loader2,
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { OptionsPanel } from "./OptionsPanel";
import type { GenerateRequest } from "@/types";

interface ScriptInputFormProps {
  onSubmit: (data: GenerateRequest) => void;
  isLoading: boolean;
  error?: string | null;
}

export function ScriptInputForm({
  onSubmit,
  isLoading,
  error,
}: ScriptInputFormProps) {
  const [script, setScript] = useState("");
  const [targetUrl, setTargetUrl] = useState("");
  const [showCredentials, setShowCredentials] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Options
  const [outputFormats, setOutputFormats] = useState<
    ("markdown" | "html" | "pdf")[]
  >(["markdown", "pdf"]);
  const [language, setLanguage] = useState("en");
  const [domainHint, setDomainHint] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!script.trim() || !targetUrl.trim()) return;

    const payload: GenerateRequest = {
      script: script.trim(),
      target_url: targetUrl.trim(),
      options: {
        output_formats: outputFormats,
        language,
        domain_hint: domainHint.trim() || undefined,
      },
    };

    if (username.trim() || password.trim()) {
      payload.credentials = {
        username: username.trim(),
        password: password.trim(),
      };
    }

    // Discard credentials from local form state immediately after dispatch
    setUsername("");
    setPassword("");
    setShowCredentials(false);

    onSubmit(payload);
  };

  const isFormValid = script.trim().length >= 10 && targetUrl.trim().length > 0;

  return (
    <Card className="w-full max-w-4xl mx-auto shadow-md border-border">
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-brand/10 text-brand">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <CardTitle className="text-xl">Generate User Manual</CardTitle>
            <CardDescription>
              Input workflow steps and staging URL. DocuAgent will autonomously
              navigate, capture UI highlights, and draft standard technical
              documentation.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {error && (
            <div className="flex items-center gap-3 p-3 text-sm rounded-lg bg-destructive/15 text-destructive border border-destructive/20">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Workflow Script */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <Label
                htmlFor="script"
                className="text-sm font-semibold flex items-center gap-1.5"
              >
                <FileCode className="h-4 w-4 text-brand" /> Workflow Script
              </Label>
              <span className="text-xs text-muted-foreground">
                {script.length} characters (min 10)
              </span>
            </div>
            <Textarea
              id="script"
              rows={6}
              placeholder="e.g. 1. Go to Login page and enter credentials. 2. Navigate to Customers tab. 3. Click 'Add New Customer' button and fill the form with test data. 4. Click Save and confirm notification banner appears."
              value={script}
              onChange={(e) => setScript(e.target.value)}
              className="font-mono text-sm leading-relaxed"
              required
            />
          </div>

          {/* Staging URL */}
          <div className="space-y-2">
            <Label
              htmlFor="targetUrl"
              className="text-sm font-semibold flex items-center gap-1.5"
            >
              <Globe className="h-4 w-4 text-brand" /> Target Application URL
            </Label>
            <Input
              id="targetUrl"
              type="url"
              placeholder="https://staging.app.example.com"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              className="font-mono text-sm"
              required
            />
          </div>

          {/* Collapsible Credentials */}
          <div className="border rounded-lg p-3 bg-muted/20">
            <button
              type="button"
              className="flex items-center justify-between w-full text-left font-medium text-sm text-foreground hover:text-brand transition-colors"
              onClick={() => setShowCredentials(!showCredentials)}
            >
              <div className="flex items-center gap-2">
                <Lock className="h-4 w-4 text-muted-foreground" />
                <span>Authentication Credentials (Optional)</span>
              </div>
              {showCredentials ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </button>

            {showCredentials && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3 pt-3 border-t">
                <div className="space-y-1">
                  <Label htmlFor="username" className="text-xs">
                    Username / Email
                  </Label>
                  <Input
                    id="username"
                    type="text"
                    autoComplete="off"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="admin@example.com"
                    className="h-9"
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="password" className="text-xs">
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    autoComplete="new-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="h-9"
                  />
                </div>
                <p className="text-[11px] text-muted-foreground col-span-full">
                  🔒 Handled ephemerally in memory during automation and
                  strictly excluded from logs and storage.
                </p>
              </div>
            )}
          </div>

          {/* Options Panel */}
          <OptionsPanel
            outputFormats={outputFormats}
            onChangeFormats={setOutputFormats}
            language={language}
            onChangeLanguage={setLanguage}
            domainHint={domainHint}
            onChangeDomainHint={setDomainHint}
          />
        </CardContent>

        <CardFooter className="flex justify-between border-t pt-5">
          <p className="text-xs text-muted-foreground">
            Fast Playwright execution with real-time UI highlight borders.
          </p>
          <Button
            type="submit"
            disabled={!isFormValid || isLoading}
            className="min-w-[160px] bg-brand text-black hover:bg-brand/90 font-semibold"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Generate Manual
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
