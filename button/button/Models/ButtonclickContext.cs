using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace button.Models;

public partial class ButtonclickContext : DbContext
{
    public ButtonclickContext(DbContextOptions<ButtonclickContext> options)
        : base(options)
    {
    }

    public virtual DbSet<TopMenu> TopMenu { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<TopMenu>(entity =>
        {
            entity.HasKey(e => e.ClickID).HasName("PK_buttoncount");

            entity.Property(e => e.ClickID).ValueGeneratedNever();
            entity.Property(e => e.ButtonType)
                .HasMaxLength(10)
                .IsFixedLength();
            entity.Property(e => e.ClickTime).HasColumnType("datetime");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
