using System.ComponentModel.DataAnnotations;

namespace AutoSender.Models
{
    public class ContatoModel
    {
        public int Id { get; set; }

        [Required]
        public string Nome { get; set; }

        [Required]
        [Phone]
        public string NumeroTelefone { get; set; } 
        public string Mensagem { get; set; } = string.Empty;
    }
}
