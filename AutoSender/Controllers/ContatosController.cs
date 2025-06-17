using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using AutoSender.Data;
using AutoSender.Models;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using System.IO;

namespace AutoSender.Controllers
{
    public class ContatosController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly ILogger<ContatosController> _logger;

        public ContatosController(ApplicationDbContext context, ILogger<ContatosController> logger)
        {
            _context = context;
            _logger = logger;
        }

        // GET: Contatos
        public async Task<IActionResult> Index()
        {
            try
            {
                var contatos = await _context.Contatos
                    .OrderByDescending(c => c.DataCadastro)
                    .ToListAsync();
                return View(contatos);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro ao listar contatos");
                TempData["Erro"] = "Ocorreu um erro ao listar os contatos.";
                return View(new List<Contato>());
            }
        }

        // GET: Contatos/Create
        public IActionResult Create()
        {
            return View();
        }

        // POST: Contatos/Create
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create([Bind("Nome,Telefone,MensagemPersonalizada")] Contato contato)
        {
            try
            {
                if (ModelState.IsValid)
                {
                    contato.DataCadastro = DateTime.UtcNow;
                    _context.Add(contato);
                    await _context.SaveChangesAsync();
                    TempData["Sucesso"] = "Contato cadastrado com sucesso!";
                    return RedirectToAction(nameof(Index));
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro ao criar contato");
                ModelState.AddModelError("", "Ocorreu um erro ao salvar o contato.");
            }
            return View(contato);
        }

        // GET: Contatos/Edit/5
        public async Task<IActionResult> Edit(int? id)
        {
            if (id == null)
            {
                return NotFound();
            }

            var contato = await _context.Contatos.FindAsync(id);
            if (contato == null)
            {
                return NotFound();
            }
            return View(contato);
        }

        // POST: Contatos/Edit/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, [Bind("Id,Nome,Telefone,MensagemPersonalizada")] Contato contato)
        {
            if (id != contato.Id)
            {
                return NotFound();
            }

            try
            {
                if (ModelState.IsValid)
                {
                    var contatoExistente = await _context.Contatos.FindAsync(id);
                    if (contatoExistente == null)
                    {
                        return NotFound();
                    }

                    contatoExistente.Nome = contato.Nome;
                    contatoExistente.Telefone = contato.Telefone;
                    contatoExistente.MensagemPersonalizada = contato.MensagemPersonalizada;

                    await _context.SaveChangesAsync();
                    TempData["Sucesso"] = "Contato atualizado com sucesso!";
                    return RedirectToAction(nameof(Index));
                }
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!ContatoExists(contato.Id))
                {
                    return NotFound();
                }
                else
                {
                    throw;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro ao editar contato");
                ModelState.AddModelError("", "Ocorreu um erro ao atualizar o contato.");
            }
            return View(contato);
        }

        // GET: Contatos/Delete/5
        public async Task<IActionResult> Delete(int? id)
        {
            if (id == null)
            {
                return NotFound();
            }

            var contato = await _context.Contatos
                .FirstOrDefaultAsync(m => m.Id == id);
            if (contato == null)
            {
                return NotFound();
            }

            return View(contato);
        }

        // POST: Contatos/Delete/5
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            try
            {
                var contato = await _context.Contatos.FindAsync(id);
                if (contato != null)
                {
                    _context.Contatos.Remove(contato);
                    await _context.SaveChangesAsync();
                    TempData["Sucesso"] = "Contato excluído com sucesso!";
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro ao excluir contato");
                TempData["Erro"] = "Ocorreu um erro ao excluir o contato.";
            }
            return RedirectToAction(nameof(Index));
        }

        // GET: Contatos/Automacao
        public async Task<IActionResult> Automacao()
        {
            try
            {
                var contatos = await _context.Contatos
                    .OrderByDescending(c => c.DataCadastro)
                    .ToListAsync();
                return View(contatos);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro ao carregar página de automação");
                TempData["Erro"] = "Ocorreu um erro ao carregar os contatos.";
                return View(new List<Contato>());
            }
        }

        // POST: Contatos/ExecutarAutomacao
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult ExecutarAutomacao()
        {
            try
            {
                var pythonPath = "python"; // ou o caminho completo para o Python
                var scriptPath = Path.Combine(Directory.GetCurrentDirectory(), "..", "WhatsAppService", "whatsapp_sender.py");
                
                var startInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = scriptPath,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = System.Diagnostics.Process.Start(startInfo))
                {
                    var output = process.StandardOutput.ReadToEnd();
                    var error = process.StandardError.ReadToEnd();
                    process.WaitForExit();

                    if (process.ExitCode == 0)
                    {
                        TempData["Sucesso"] = "Automação executada com sucesso!";
                    }
                    else
                    {
                        _logger.LogError($"Erro na automação: {error}");
                        TempData["Erro"] = "Ocorreu um erro durante a automação. Verifique os logs.";
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro ao executar automação");
                TempData["Erro"] = "Ocorreu um erro ao executar a automação.";
            }

            return RedirectToAction(nameof(Automacao));
        }

        private bool ContatoExists(int id)
        {
            return _context.Contatos.Any(e => e.Id == id);
        }
    }
} 