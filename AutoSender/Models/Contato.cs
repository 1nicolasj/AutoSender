using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AutoSender.Models
{
    public class Contato
    {
        public int Id { get; set; }

        [Required(ErrorMessage = "O nome é obrigatório")]
        [Display(Name = "Nome")]
        [StringLength(100, ErrorMessage = "O nome deve ter no máximo 100 caracteres")]
        public string Nome { get; set; } = string.Empty;

        [Required(ErrorMessage = "O telefone é obrigatório")]
        [Display(Name = "Telefone")]
        [RegularExpression(@"^\+?[1-9]\d{1,14}$", ErrorMessage = "Formato de telefone inválido. Use o formato: +5511999999999")]
        [StringLength(15, ErrorMessage = "O telefone deve ter no máximo 15 caracteres")]
        public string Telefone { get; set; } = string.Empty;

        [Required(ErrorMessage = "A mensagem é obrigatória")]
        [Display(Name = "Mensagem Personalizada")]
        [StringLength(1000, ErrorMessage = "A mensagem deve ter no máximo 1000 caracteres")]
        public string MensagemPersonalizada { get; set; } = string.Empty;

        [Display(Name = "Data de Cadastro")]
        [Column(TypeName = "timestamp with time zone")]
        public DateTime DataCadastro { get; set; } = DateTime.UtcNow;
    }
} 