using Microsoft.SemanticKernel;
using System.ComponentModel;
using System.Net.Http;
using System.Text.Json;

public class AgentHubPlugin
{
    private readonly HttpClient _httpClient;
    private const string BaseUrl = "https://web-production-4833.up.railway.app";

    public AgentHubPlugin()
    {
        _httpClient = new HttpClient();
    }

    [KernelFunction, Description("Analyze sentiment of text using Agent Hub")]
    public async Task<string> AnalyzeSentiment(
        [Description("Text to analyze")] string text,
        [Description("USDC payment transaction hash")] string? paymentTx = null)
    {
        var payload = new { text };
        var request = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/agent/sentiment")
        {
            Content = JsonContent.Create(payload)
        };
        
        if (!string.IsNullOrEmpty(paymentTx))
            request.Headers.Add("PAYMENT-SIGNATURE", paymentTx);

        var response = await _httpClient.SendAsync(request);
        return await response.Content.ReadAsStringAsync();
    }

    [KernelFunction, Description("Translate text to target language")]
    public async Task<string> Translate(
        [Description("Text to translate")] string text,
        [Description("Target language")] string targetLanguage,
        [Description("USDC payment transaction hash")] string? paymentTx = null)
    {
        var payload = new { text, target_language = targetLanguage };
        var request = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/agent/translate")
        {
            Content = JsonContent.Create(payload)
        };
        
        if (!string.IsNullOrEmpty(paymentTx))
            request.Headers.Add("PAYMENT-SIGNATURE", paymentTx);

        var response = await _httpClient.SendAsync(request);
        return await response.Content.ReadAsStringAsync();
    }

    [KernelFunction, Description("Perform web research using Agent Hub")]
    public async Task<string> Research(
        [Description("Research query")] string query,
        [Description("Maximum number of sources")] int maxSources = 5,
        [Description("USDC payment transaction hash")] string? paymentTx = null)
    {
        var payload = new { query, max_sources = maxSources };
        var request = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/agent/research")
        {
            Content = JsonContent.Create(payload)
        };
        
        if (!string.IsNullOrEmpty(paymentTx))
            request.Headers.Add("PAYMENT-SIGNATURE", paymentTx);

        var response = await _httpClient.SendAsync(request);
        return await response.Content.ReadAsStringAsync();
    }

    [KernelFunction, Description("Scrape web page content")]
    public async Task<string> ScrapeWeb(
        [Description("URL to scrape")] string url,
        [Description("USDC payment transaction hash")] string? paymentTx = null)
    {
        var payload = new { url };
        var request = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/agent/scrape")
        {
            Content = JsonContent.Create(payload)
        };
        
        if (!string.IsNullOrEmpty(paymentTx))
            request.Headers.Add("PAYMENT-SIGNATURE", paymentTx);

        var response = await _httpClient.SendAsync(request);
        return await response.Content.ReadAsStringAsync();
    }

    [KernelFunction, Description("Generate content with AI")]
    public async Task<string> GenerateContent(
        [Description("Content topic")] string topic,
        [Description("Content type")] string contentType = "article",
        [Description("Writing tone")] string tone = "professional",
        [Description("Target word count")] int wordCount = 500,
        [Description("USDC payment transaction hash")] string? paymentTx = null)
    {
        var payload = new { topic, content_type = contentType, tone, word_count = wordCount };
        var request = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/agent/content-gen")
        {
            Content = JsonContent.Create(payload)
        };
        
        if (!string.IsNullOrEmpty(paymentTx))
            request.Headers.Add("PAYMENT-SIGNATURE", paymentTx);

        var response = await _httpClient.SendAsync(request);
        return await response.Content.ReadAsStringAsync();
    }

    [KernelFunction, Description("Review code for security and performance")]
    public async Task<string> ReviewCode(
        [Description("Code to review")] string code,
        [Description("Programming language")] string language,
        [Description("Check security")] bool checkSecurity = true,
        [Description("Check performance")] bool checkPerformance = true,
        [Description("USDC payment transaction hash")] string? paymentTx = null)
    {
        var payload = new { code, language, check_security = checkSecurity, check_performance = checkPerformance };
        var request = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/agent/code-review")
        {
            Content = JsonContent.Create(payload)
        };
        
        if (!string.IsNullOrEmpty(paymentTx))
            request.Headers.Add("PAYMENT-SIGNATURE", paymentTx);

        var response = await _httpClient.SendAsync(request);
        return await response.Content.ReadAsStringAsync();
    }
}
